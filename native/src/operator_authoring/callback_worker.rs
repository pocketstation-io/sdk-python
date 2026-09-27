//! Bound blocking Python callbacks independently of Core's async runtime.
//!
//! Each node has one worker and one queued command. A callback cannot be forcibly
//! interrupted; its admission permit stays owned until the thread actually exits.
//! The process-wide cap prevents repeated timed-out callbacks growing unbounded.
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{mpsc, Arc};
use std::thread::JoinHandle;

use pocketstation::NodeError;
use pyo3::prelude::*;
use tokio::sync::oneshot;

use super::values::PythonOperatorEmission;

const MAXIMUM_CALLBACK_WORKERS: usize = 64;
static ACTIVE_WORKERS: AtomicUsize = AtomicUsize::new(0);
type CallbackResult = Result<Vec<PythonOperatorEmission>, NodeError>;
type Callback = Box<dyn FnOnce(&Py<PyAny>) -> CallbackResult + Send>;
struct Request {
    callback: Callback,
    reply: oneshot::Sender<CallbackResult>,
    close: bool,
}
struct WorkerPermit;
impl WorkerPermit {
    fn acquire() -> Result<Self, NodeError> {
        ACTIVE_WORKERS
            .fetch_update(Ordering::AcqRel, Ordering::Acquire, |active| {
                (active < MAXIMUM_CALLBACK_WORKERS).then_some(active + 1)
            })
            .map(|_| Self)
            .map_err(|_| {
                NodeError::Process("Python operator callback worker capacity exhausted".to_owned())
            })
    }
}
impl Drop for WorkerPermit {
    fn drop(&mut self) {
        ACTIVE_WORKERS.fetch_sub(1, Ordering::AcqRel);
    }
}

pub(super) struct CallbackWorker {
    sender: Option<mpsc::SyncSender<Request>>,
    join: Option<JoinHandle<()>>,
    closed: Arc<std::sync::atomic::AtomicBool>,
}

impl CallbackWorker {
    pub(super) fn new(node: Py<PyAny>) -> Result<Self, NodeError> {
        let permit = WorkerPermit::acquire()?;
        let (sender, receiver) = mpsc::sync_channel::<Request>(1);
        let closed = Arc::new(std::sync::atomic::AtomicBool::new(false));
        let worker_closed = Arc::clone(&closed);
        let join = std::thread::Builder::new()
            .name("pks-python-operator".to_owned())
            .spawn(move || {
                let _permit = permit;
                let mut explicitly_closed = false;
                while let Ok(request) = receiver.recv() {
                    let result = (request.callback)(&node);
                    if request.close {
                        explicitly_closed = true;
                        worker_closed.store(true, Ordering::Release);
                        let _ = request.reply.send(result);
                        break;
                    }
                    let _ = request.reply.send(result);
                }
                if !explicitly_closed {
                    // Dropped/failed owners relinquish the mailbox, never the callback
                    // thread. Close only after the last synchronous callback returns.
                    Python::attach(|py| {
                        let _ = node.bind(py).call_method0("close");
                    });
                    worker_closed.store(true, Ordering::Release);
                }
            })
            .map_err(|error| {
                NodeError::Process(format!(
                    "cannot start Python operator callback worker: {error}"
                ))
            })?;
        Ok(Self {
            sender: Some(sender),
            join: Some(join),
            closed,
        })
    }

    pub(super) async fn call(&self, callback: Callback) -> CallbackResult {
        self.request(callback, false)?
            .await
            .map_err(|_| NodeError::Process("Python operator callback worker stopped".to_owned()))?
    }

    fn request(
        &self,
        callback: Callback,
        close: bool,
    ) -> Result<oneshot::Receiver<CallbackResult>, NodeError> {
        let sender = self.sender.as_ref().ok_or_else(|| {
            NodeError::Process("Python operator callback worker is closed".to_owned())
        })?;
        let (reply, receiver) = oneshot::channel();
        sender
            .try_send(Request {
                callback,
                reply,
                close,
            })
            .map_err(|_| {
                NodeError::Process(
                    "Python operator callback worker unavailable or callback still pending"
                        .to_owned(),
                )
            })?;
        Ok(receiver)
    }

    pub(super) async fn close(&mut self) -> Result<(), NodeError> {
        if self.closed.load(Ordering::Acquire) {
            return self.join_completed();
        }
        let receiver = self.request(
            Box::new(|node| {
                Python::attach(|py| {
                    node.bind(py)
                        .call_method0("close")
                        .map(|_| Vec::new())
                        .map_err(super::driver::node_process_error)
                })
            }),
            true,
        )?;
        // The terminal command is already retained even if this future times out.
        self.sender.take();
        let result = receiver.await.map_err(|_| {
            NodeError::Process("Python operator callback worker stopped before close".to_owned())
        })?;
        self.join_completed()?;
        result.map(|_| ())
    }

    fn join_completed(&mut self) -> Result<(), NodeError> {
        if let Some(join) = self.join.take() {
            join.join().map_err(|_| {
                NodeError::Process("Python operator callback worker panicked".to_owned())
            })?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn permits_remain_bounded_until_worker_ownership_really_ends() {
        let mut held = Vec::new();
        while let Ok(permit) = WorkerPermit::acquire() {
            held.push(permit);
        }
        assert_eq!(held.len(), MAXIMUM_CALLBACK_WORKERS);
        assert!(WorkerPermit::acquire().is_err());
        let permit = held.pop().expect("one occupied worker");
        let (release, wait) = mpsc::sync_channel::<()>(1);
        let worker = std::thread::spawn(move || {
            let _permit = permit;
            let _ = wait.recv();
        });
        assert!(WorkerPermit::acquire().is_err());
        release
            .send(())
            .expect("worker retained its release mailbox");
        worker.join().expect("worker exited");
        held.push(WorkerPermit::acquire().expect("actual exit releases capacity"));
        drop(held);
        assert_eq!(ACTIVE_WORKERS.load(Ordering::Acquire), 0);
    }
}
