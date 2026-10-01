"""One frame-draining Operator per stem feeding one bounded inference Operator."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import replace
from typing import TYPE_CHECKING

from pocketstation.aio.session import Session as AsyncSession
from pocketstation.graph import (
    BackpressurePolicy,
    CopyPolicy,
    DeliveryPolicy,
    DerivedStream,
    LossPolicy,
    Multiplicity,
    OperatorConfiguration,
    PortSpec,
    SourceOutput,
    Stem,
)
from pocketstation.operator_authoring import (
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorProvider,
)
from pocketstation.signal import BusSubscription, SignalEnvelope

from .audio_windows import AudioWindow, AudioWindowBuffer
from .transcript import TRANSCRIPT_SIGNAL
from .window_signal import WINDOW_SIGNAL, decode_window, encode_window

if TYPE_CHECKING:
    from .faster_whisper import (
        AudioConverter,
        FasterWhisper,
        FasterWhisperConfiguration,
        WhisperModel,
    )


class _NodeFactory:
    def __init__(self, create: Callable[[], OperatorNode]) -> None:
        self._create = create

    def create(self, _configuration: Mapping[str, str]) -> OperatorNode:
        return self._create()


class _ConfiguredNodeFactory:
    def __init__(self, create: Callable[[Mapping[str, str]], OperatorNode]) -> None:
        self._create = create

    def create(self, configuration: Mapping[str, str]) -> OperatorNode:
        return self._create(configuration)


class _TranscriptMergeNode(OperatorNode):
    def process(
        self, input_port: str, envelope: SignalEnvelope[object]
    ) -> tuple[OperatorEmission, ...]:
        if input_port != "transcript" or not isinstance(envelope.payload, str):
            raise ValueError("expected transcript text")
        return (OperatorEmission.text(envelope.payload, signal=TRANSCRIPT_SIGNAL),)


class _WindowNode(OperatorNode):
    def __init__(
        self, configuration: FasterWhisperConfiguration, converter: AudioConverter
    ) -> None:
        self._windows = AudioWindowBuffer(
            window_seconds=configuration.window_seconds,
            maximum_sources=configuration.maximum_sources,
        )
        self._converter = converter

    def process(
        self, input_port: str, envelope: SignalEnvelope[object]
    ) -> tuple[OperatorEmission, ...]:
        if input_port != "audio":
            raise ValueError("unexpected transcription window input")
        return self._emit(self._windows.push(envelope))

    def flush(self) -> tuple[OperatorEmission, ...]:
        return self._emit(self._windows.flush())

    def _emit(self, windows: Sequence[AudioWindow]) -> tuple[OperatorEmission, ...]:
        return tuple(
            OperatorEmission.bytes(
                encode_window(window, self._converter(window)), signal=WINDOW_SIGNAL
            )
            for window in windows
        )

    def cancel(self) -> None:
        self._windows.clear()


class _WindowInferenceNode(OperatorNode):
    def __init__(
        self,
        configuration: FasterWhisperConfiguration,
        model: WhisperModel,
        numpy_audio: bool,
    ) -> None:
        self._numpy_audio = numpy_audio
        self._configuration = configuration
        self._model = model

    def process(
        self, input_port: str, envelope: SignalEnvelope[object]
    ) -> tuple[OperatorEmission, ...]:
        if input_port != "window":
            raise ValueError("unexpected transcription inference input")
        from .faster_whisper import _numpy_audio, _transcribe_window

        window, audio, duration_ms = decode_window(envelope.payload)
        samples: object = audio
        if self._numpy_audio:
            numpy = importlib.import_module("numpy")
            samples = numpy.asarray(audio, dtype="float32")
        return (
            _transcribe_window(
                self._configuration,
                self._model,
                _numpy_audio,
                window,
                prepared_audio=samples,
                duration_ms=duration_ms,
            ),
        )


def attach_window_pipeline(
    transcriber: FasterWhisper,
    session: AsyncSession,
    streams: Iterable[Stem | SourceOutput | DerivedStream],
) -> BusSubscription[str]:
    from .faster_whisper import _numpy_audio

    selected = tuple(streams)
    if not selected:
        raise ValueError("transcription requires at least one input stream")
    if len(selected) > transcriber.configuration.maximum_sources:
        raise ValueError("maximum transcription sources exceeded")
    window_manifest = OperatorManifest(
        "community.faster-whisper.windows.v1",
        inputs=transcriber.manifest.inputs,
        outputs=(PortSpec.output("window", WINDOW_SIGNAL),),
        queue_capacity_signals=transcriber.configuration.queue_capacity_signals,
        drain_queued=False,
    )
    window_registration = session.register_operator(
        OperatorProvider.with_node(
            window_manifest,
            _NodeFactory(
                lambda: _WindowNode(
                    transcriber.configuration, transcriber._audio_converter
                )
            ),
        )
    )
    windows_by_stream = [window_registration.declare() for _ in selected]
    inference_manifest = OperatorManifest(
        "community.faster-whisper.inference.v1",
        inputs=(
            PortSpec.input("window", WINDOW_SIGNAL, multiplicity=Multiplicity.MANY),
        ),
        outputs=transcriber.manifest.outputs,
        queue_capacity_signals=8,
        process_timeout_ms=transcriber.manifest.process_timeout_ms,
        network_allowed=transcriber.manifest.network_allowed,
        filesystem_allowed=True,
        drain_queued=False,
        terminal_roles=transcriber.manifest.terminal_roles,
        # Slow inference may discard complete input windows; transcript output
        # remains required. Keep that product policy explicit in the graph.
        input_delivery=(
            DeliveryPolicy.bounded_async()
            .with_loss(LossPolicy.DROP_ALLOWED)
            .with_backpressure(BackpressurePolicy.DROP_NEWEST)
            .with_copy_policy(CopyPolicy.COPY_TO_BRANCH_POOL)
        ),
    )
    configuration = transcriber.configuration
    worker_count = min(configuration.inference_concurrency, len(selected))
    quotient, remainder = divmod(configuration.cpu_threads, worker_count)
    configurations = tuple(
        replace(
            configuration,
            inference_concurrency=1,
            cpu_threads=quotient + (1 if index < remainder else 0),
        )
        for index in range(worker_count)
    )

    def create_inference(values: Mapping[str, str]) -> OperatorNode:
        worker_index = int(values["worker_index"])
        if not 0 <= worker_index < worker_count:
            raise ValueError("invalid inference worker index")
        worker_configuration = configurations[worker_index]
        return _WindowInferenceNode(
            worker_configuration,
            transcriber._model_factory(worker_configuration),
            transcriber._audio_converter is _numpy_audio,
        )

    inference_registration = session.register_operator(
        OperatorProvider.with_node(
            inference_manifest,
            _ConfiguredNodeFactory(create_inference),
        )
    )
    inference = tuple(
        inference_registration.declare(
            OperatorConfiguration({"worker_index": str(index)})
        )
        for index in range(worker_count)
    )
    for index, (stream, windows) in enumerate(
        zip(selected, windows_by_stream, strict=True)
    ):
        stream.connect(windows.input("audio"))
        windows.output("window").connect(
            inference[index % worker_count].input("window")
        )
    if worker_count == 1:
        return session.subscribe(
            inference[0].output("transcript"), signal=TRANSCRIPT_SIGNAL
        )
    merge = session.register_operator(
        OperatorProvider.with_node(
            OperatorManifest(
                "community.faster-whisper.transcripts.v1",
                inputs=(
                    PortSpec.input(
                        "transcript", TRANSCRIPT_SIGNAL, multiplicity=Multiplicity.MANY
                    ),
                ),
                outputs=transcriber.manifest.outputs,
                queue_capacity_signals=8,
                drain_queued=False,
                terminal_roles=transcriber.manifest.terminal_roles,
            ),
            _NodeFactory(_TranscriptMergeNode),
        )
    ).declare()
    for worker in inference:
        worker.output("transcript").connect(merge.input("transcript"))
    return session.subscribe(merge.output("transcript"), signal=TRANSCRIPT_SIGNAL)
