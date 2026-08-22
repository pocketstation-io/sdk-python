"""Create and operate PocketStation RelaySessions with asyncio."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from time import monotonic
from types import TracebackType
from typing import TYPE_CHECKING

from ..control import SessionCredentials, SessionId, SessionSnapshot
from ..errors import _native_call
from ..relay import (
    PublisherActivation,
    ReceiverActivation,
    ReceiverInvitation,
    RelayError,
    RelayPublisher,
    RelayTimeoutError,
    _bounded_request_timeout,
    _normalize_relay_url,
    _receiver_invitation,
    _validate_request_timeout,
    _validate_wait,
)
from .control import ControlClient

if TYPE_CHECKING:
    from .session import Session


class RelaySession:
    """Async owner of one remote Session and bounded control clients."""

    def __init__(
        self,
        *,
        relay_url: str,
        credentials: SessionCredentials,
        control: ControlClient,
        owns_control: bool,
        request_timeout_seconds: float,
    ) -> None:
        self.relay_url = _normalize_relay_url(relay_url)
        self.credentials = credentials
        self._control = control
        self._owns_control = owns_control
        self._request_timeout_seconds = request_timeout_seconds
        self._publisher_activation: PublisherActivation | None = None
        self._invitation: ReceiverInvitation | None = None
        self._receiver_activation: ReceiverActivation | None = None
        self._closed = False

    @classmethod
    async def create(
        cls,
        *,
        control_plane_url: str,
        relay_url: str,
        request_timeout_seconds: float = 10.0,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        control_client: ControlClient | None = None,
    ) -> RelaySession:
        request_timeout_seconds = _validate_request_timeout(request_timeout_seconds)
        normalized_relay_url = _normalize_relay_url(relay_url)
        owns_control = control_client is None
        control = control_client or ControlClient(
            control_plane_url,
            timeout_seconds=request_timeout_seconds,
        )
        try:
            credentials = await control.create_session(
                required_buses=required_buses,
                timeout_seconds=request_timeout_seconds,
            )
        except BaseException:
            if owns_control:
                await control.aclose()
            raise
        return cls(
            relay_url=normalized_relay_url,
            credentials=credentials,
            control=control,
            owns_control=owns_control,
            request_timeout_seconds=request_timeout_seconds,
        )

    @property
    def session_id(self) -> SessionId:
        return self.credentials.session_id

    @property
    def publisher_activation(self) -> PublisherActivation | None:
        return self._publisher_activation

    @property
    def invitation(self) -> ReceiverInvitation | None:
        return self._invitation

    @property
    def receiver_activation(self) -> ReceiverActivation | None:
        return self._receiver_activation

    def publisher(self, session: Session) -> RelayPublisher:
        """Declare the same native relay endpoint used by the sync namespace."""
        self._require_open()
        native = _native_call(
            lambda: session._native.relay(
                self.relay_url,
                str(self.session_id),
                self.credentials.source_token.expose_secret(),
            )
        )
        return RelayPublisher(
            native,
            relay_url=self.relay_url,
            session_id=self.session_id,
        )

    async def wait_for_publisher(
        self,
        *,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> PublisherActivation:
        self._require_open()
        snapshot = await self._wait_for_snapshot(
            lambda value: value.ready,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.publisher_timeout",
            timeout_message="relay publisher did not become active before the deadline",
        )
        activation = PublisherActivation(snapshot)
        self._publisher_activation = activation
        return activation

    async def create_receiver_invitation(
        self, *, bus_id: str = "mix"
    ) -> ReceiverInvitation:
        self._require_open()
        if self._publisher_activation is None:
            raise RelayError(
                "wait_for_publisher() must succeed before creating an invitation",
                "relay.publisher_not_active",
            )
        created = await self._control.create_invitation(
            self.session_id,
            self.credentials.source_token,
            bus_id=bus_id,
            timeout_seconds=self._request_timeout_seconds,
        )
        invitation = _receiver_invitation(created, self.session_id)
        self._invitation = invitation
        return invitation

    async def wait_for_publisher_and_invitation(
        self,
        *,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverInvitation:
        await self.wait_for_publisher(
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        return await self.create_receiver_invitation()

    async def wait_for_receiver(
        self,
        *,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverActivation:
        self._require_open()
        if self._invitation is None:
            raise RelayError(
                "create_receiver_invitation() must succeed before waiting "
                "for a receiver",
                "relay.invitation_missing",
            )
        snapshot = await self._wait_for_snapshot(
            lambda value: value.ready and value.subscription_count > 0,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.receiver_timeout",
            timeout_message="relay receiver did not become active before the deadline",
        )
        activation = ReceiverActivation(snapshot)
        self._receiver_activation = activation
        return activation

    async def aclose(self, *, delete_remote_session: bool = True) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if delete_remote_session:
                await self._control.delete_session(
                    self.session_id,
                    self.credentials.source_token,
                    timeout_seconds=self._request_timeout_seconds,
                )
        finally:
            if self._owns_control:
                await self._control.aclose()

    async def __aenter__(self) -> RelaySession:
        self._require_open()
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return (
            "aio.RelaySession("
            f"session_id={self.session_id!r}, relay_url={self.relay_url!r}, "
            "credentials=[redacted])"
        )

    async def _wait_for_snapshot(
        self,
        predicate: Callable[[SessionSnapshot], bool],
        *,
        timeout_seconds: float,
        poll_interval_seconds: float,
        timeout_code: str,
        timeout_message: str,
    ) -> SessionSnapshot:
        _validate_wait(timeout_seconds, poll_interval_seconds)
        deadline = monotonic() + timeout_seconds
        while True:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise RelayTimeoutError(timeout_message, timeout_code)
            snapshot = await self._control.session(
                self.session_id,
                self.credentials.source_token,
                timeout_seconds=_bounded_request_timeout(
                    remaining,
                    self._request_timeout_seconds,
                ),
            )
            if predicate(snapshot):
                return snapshot
            await asyncio.sleep(
                min(poll_interval_seconds, max(0.0, deadline - monotonic()))
            )

    def _require_open(self) -> None:
        if self._closed:
            raise RelayError("RelaySession has closed", "relay.closed")


__all__ = [
    "PublisherActivation",
    "ReceiverActivation",
    "ReceiverInvitation",
    "RelayError",
    "RelayPublisher",
    "RelaySession",
    "RelayTimeoutError",
]
