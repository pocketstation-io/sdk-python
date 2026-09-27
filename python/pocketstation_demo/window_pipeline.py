"""One frame-draining Operator per stem feeding one bounded inference Operator."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING

from pocketstation.aio.session import Session as AsyncSession
from pocketstation.graph import (
    DerivedStream,
    Multiplicity,
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
    )
    inference = session.register_operator(
        OperatorProvider.with_node(
            inference_manifest,
            _NodeFactory(
                lambda: _WindowInferenceNode(
                    transcriber.configuration,
                    transcriber._model_factory(transcriber.configuration),
                    transcriber._audio_converter is _numpy_audio,
                )
            ),
        )
    ).declare()
    for stream, windows in zip(selected, windows_by_stream, strict=True):
        stream.connect(windows.input("audio"))
        windows.output("window").connect(inference.input("window"))
    return session.subscribe(inference.output("transcript"), signal=TRANSCRIPT_SIGNAL)
