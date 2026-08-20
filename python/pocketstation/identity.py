"""Zero-overhead nominal identities used by the native Session runtime."""

from typing import Literal, NewType, TypeAlias

# ``SessionId`` already names the opaque Relay control-plane identifier in the
# public API. RuntimeSessionId deliberately distinguishes the numeric Core
# execution identity instead of letting unrelated identifiers type-check.
RuntimeSessionId = NewType("RuntimeSessionId", int)
StreamId = NewType("StreamId", int)
SourceId = NewType("SourceId", int)
SourceInstanceId = NewType("SourceInstanceId", int)
StemId = NewType("StemId", int)
ClockDomainId = NewType("ClockDomainId", int)
ClockDomainKind: TypeAlias = Literal[
    "unspecified", "process-monotonic", "provider-defined"
]
ClockDomainOrigin: TypeAlias = Literal[
    "unspecified", "process-start", "provider-defined"
]
EndpointId = NewType("EndpointId", int)
ConnectorId = NewType("ConnectorId", int)
RouteId = NewType("RouteId", int)
OperatorInstanceId = NewType("OperatorInstanceId", int)
SidecarId = NewType("SidecarId", int)

__all__ = [
    "ClockDomainId",
    "ClockDomainKind",
    "ClockDomainOrigin",
    "ConnectorId",
    "EndpointId",
    "OperatorInstanceId",
    "RouteId",
    "RuntimeSessionId",
    "SidecarId",
    "SourceId",
    "SourceInstanceId",
    "StemId",
    "StreamId",
]
