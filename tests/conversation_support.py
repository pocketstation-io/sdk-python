from __future__ import annotations

from collections.abc import Iterator
from threading import Event

from pocketstation._api import (
    MediaCaps,
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorProvider,
    PortSpec,
    SignalEnvelope,
    SignalSpec,
    SourceEmission,
    SourceManifest,
    SourceProvider,
)

TRANSCRIPT_SIGNAL = SignalSpec.text(role="transcript.final")


def transcript_source(*texts: str) -> SourceProvider:
    def emissions() -> Iterator[SourceEmission]:
        for text in texts:
            yield SourceEmission.text(
                "transcript",
                text,
                signal=TRANSCRIPT_SIGNAL,
            )

    return SourceProvider.from_iterable(
        SourceManifest(
            "io.pocketstation.source.conversation-test.v1",
            outputs=(
                PortSpec.output(
                    "transcript",
                    TRANSCRIPT_SIGNAL,
                    media=MediaCaps.text(),
                ),
            ),
        ),
        lambda _configuration: emissions(),
    )


def transcript_source_after(
    first: str,
    second: str,
    *,
    ready: Event,
    timeout_s: float = 5,
) -> SourceProvider:
    """Emit the second transcript after a finite external readiness gate."""

    def emissions() -> Iterator[SourceEmission]:
        yield SourceEmission.text(
            "transcript",
            first,
            signal=TRANSCRIPT_SIGNAL,
        )
        if not ready.wait(timeout_s):
            raise TimeoutError("second transcript readiness gate timed out")
        yield SourceEmission.text(
            "transcript",
            second,
            signal=TRANSCRIPT_SIGNAL,
        )

    return SourceProvider.from_iterable(
        SourceManifest(
            "io.pocketstation.source.gated-conversation-test.v1",
            outputs=(
                PortSpec.output(
                    "transcript",
                    TRANSCRIPT_SIGNAL,
                    media=MediaCaps.text(),
                ),
            ),
        ),
        lambda _configuration: emissions(),
    )


def transcript_operator() -> OperatorProvider:
    class PassTranscript(OperatorNode):
        def process(
            self,
            _input_port: str,
            envelope: SignalEnvelope[object],
        ) -> tuple[OperatorEmission, ...]:
            return (
                OperatorEmission.text(
                    str(envelope.payload),
                    signal=TRANSCRIPT_SIGNAL,
                ),
            )

    class Factory:
        def create(self, _configuration: object) -> PassTranscript:
            return PassTranscript()

    return OperatorProvider.with_node(
        OperatorManifest(
            "io.pocketstation.operator.conversation-test.v1",
            inputs=(
                PortSpec.input(
                    "transcript",
                    TRANSCRIPT_SIGNAL,
                    media=MediaCaps.text(),
                ),
            ),
            outputs=(
                PortSpec.output(
                    "transcript",
                    TRANSCRIPT_SIGNAL,
                    media=MediaCaps.text(),
                ),
            ),
            terminal_roles=("transcript.final",),
        ),
        Factory(),
    )
