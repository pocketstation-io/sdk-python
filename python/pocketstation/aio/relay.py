"""Create and operate PocketStation RelaySessions with asyncio."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from time import monotonic
from types import TracebackType
from typing import TYPE_CHECKING

from ..control import (
    ControlPlaneError,
    InvitationVisibility,
    SessionCredentials,
    SessionId,
    SessionSnapshot,
)
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
    _owner_deadline,
    _owner_failure,
    _receiver_invitation,
    _relay_publisher_ice_servers,
    _resolve_relay_url,
    _transient_owner_error,
    _validate_minimum_receivers,
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
        ice_servers: tuple[tuple[str, ...], ...],
    ) -> None:
        self.relay_url = _normalize_relay_url(relay_url)
        self.credentials = credentials
        self._control = control
        self._owns_control = owns_control
        self._request_timeout_seconds = request_timeout_seconds
        self._ice_servers = ice_servers
        self._publisher_activation: PublisherActivation | None = None
        self._invitation: ReceiverInvitation | None = None
        self._receiver_activation: ReceiverActivation | None = None
        self._closed = False
        self._cleanup_complete = False
        self._renewal_task: asyncio.Task[None] | None = None
        self._renewal_error: RelayError | None = None
        self._owner_expires_at: datetime | None = None
        self._owner_deadline = 0.0

    @classmethod
    async def create(
        cls,
        *,
        control_plane_url: str,
        relay_url: str | None = None,
        request_timeout_seconds: float = 10.0,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        control_client: ControlClient | None = None,
        maintain_owner: bool = True,
    ) -> RelaySession:
        request_timeout_seconds = _validate_request_timeout(request_timeout_seconds)
        if type(maintain_owner) is not bool:
            raise TypeError("maintain_owner must be a boolean")
        requested_relay_url = (
            None if relay_url is None else _normalize_relay_url(relay_url)
        )
        owns_control = control_client is None
        control = control_client or ControlClient(
            control_plane_url,
            timeout_seconds=request_timeout_seconds,
        )
        credentials: SessionCredentials | None = None
        try:
            credentials = await control.create_session(
                required_buses=required_buses,
                timeout_seconds=request_timeout_seconds,
            )
            normalized_relay_url = _resolve_relay_url(
                credentials,
                requested_relay_url,
            )
            ice_servers = _relay_publisher_ice_servers(credentials.ice_servers)
            remote = cls(
                relay_url=normalized_relay_url,
                credentials=credentials,
                control=control,
                owns_control=owns_control,
                request_timeout_seconds=request_timeout_seconds,
                ice_servers=ice_servers,
            )
            if maintain_owner:
                renewed = await asyncio.wait_for(
                    control.renew_session(
                        credentials.session_id,
                        credentials.source_token,
                        timeout_seconds=request_timeout_seconds,
                    ),
                    timeout=request_timeout_seconds,
                )
                deadline = _owner_deadline(renewed.expires_at)
                credentials = replace(credentials, source_token=renewed.source_token)
                remote.credentials = credentials
                remote._owner_deadline = deadline
                remote._owner_expires_at = renewed.expires_at
                remote._renewal_task = asyncio.create_task(
                    remote._renew_owner(), name="pocketstation-owner-renewal"
                )
        except BaseException as error:
            if credentials is not None:
                try:
                    await control.delete_session(
                        credentials.session_id,
                        credentials.source_token,
                        timeout_seconds=request_timeout_seconds,
                    )
                except BaseException as cleanup_error:
                    if owns_control:
                        await control.aclose()
                    raise RelayError(
                        "relay Session validation failed and remote cleanup "
                        "also failed",
                        "relay.cleanup_failed",
                    ) from BaseExceptionGroup(
                        "relay creation and cleanup failures",
                        [error, cleanup_error],
                    )
            if owns_control:
                await control.aclose()
            raise
        return remote

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
                [list(urls) for urls in self._ice_servers],
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
        self,
        *,
        bus_id: str = "mix",
        visibility: InvitationVisibility | str | None = None,
        word_count: int | None = None,
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
            visibility=visibility,
            word_count=word_count,
            timeout_seconds=self._request_timeout_seconds,
        )
        invitation = _receiver_invitation(created, self.session_id)
        self._invitation = invitation
        return invitation

    async def wait_for_publisher_and_invitation(
        self,
        *,
        bus_id: str = "mix",
        visibility: InvitationVisibility | str | None = None,
        word_count: int | None = None,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverInvitation:
        await self.wait_for_publisher(
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        return await self.create_receiver_invitation(
            bus_id=bus_id,
            visibility=visibility,
            word_count=word_count,
        )

    async def wait_for_receiver(
        self,
        *,
        minimum_receivers: int = 1,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverActivation:
        self._require_open()
        minimum_receivers = _validate_minimum_receivers(minimum_receivers)
        if self._invitation is None:
            raise RelayError(
                "create_receiver_invitation() must succeed before waiting "
                "for a receiver",
                "relay.invitation_missing",
            )
        snapshot = await self._wait_for_snapshot(
            lambda value: value.ready and value.subscription_count >= minimum_receivers,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.receiver_timeout",
            timeout_message="relay receiver did not become active before the deadline",
        )
        activation = ReceiverActivation(snapshot)
        self._receiver_activation = activation
        return activation

    @property
    def owner_expires_at(self) -> datetime | None:
        """Current owner expiry; None when lifetime is managed by the caller."""
        return self._owner_expires_at

    @property
    def renewal_error(self) -> RelayError | None:
        """Terminal owner-renewal failure, without credential diagnostics."""
        return self._renewal_error

    async def _renew_owner(self) -> None:
        try:
            while not self._closed:
                await asyncio.sleep(max(0.0, (self._owner_deadline - monotonic()) / 2))
                for attempt in range(3):
                    remaining = self._owner_deadline - monotonic()
                    if remaining <= 0:
                        self._renewal_error = _owner_failure()
                        return
                    request_timeout = min(self._request_timeout_seconds, remaining)
                    try:
                        renewed = await asyncio.wait_for(
                            self._control.renew_session(
                                self.session_id,
                                self.credentials.source_token,
                                timeout_seconds=request_timeout,
                            ),
                            timeout=request_timeout,
                        )
                        deadline = _owner_deadline(renewed.expires_at)
                        self.credentials = replace(
                            self.credentials, source_token=renewed.source_token
                        )
                        self._owner_expires_at = renewed.expires_at
                        self._owner_deadline = deadline
                        break
                    except Exception as error:
                        transient = _transient_owner_error(error) or isinstance(
                            error, TimeoutError
                        )
                    if not transient or attempt == 2:
                        self._renewal_error = _owner_failure()
                        return
                    await asyncio.sleep(
                        min(
                            0.1 * (2**attempt),
                            max(0.0, self._owner_deadline - monotonic()),
                        )
                    )
        except asyncio.CancelledError:
            return

    async def aclose(self, *, delete_remote_session: bool = True) -> None:
        if self._cleanup_complete:
            if self._renewal_error is not None:
                raise self._renewal_error
            return
        self._closed = True
        if self._renewal_task is not None:
            self._renewal_task.cancel()
            done, _ = await asyncio.wait(
                {self._renewal_task}, timeout=self._request_timeout_seconds + 1
            )
            if not done:
                self._renewal_error = RelayError(
                    "owner renewal did not stop before the shutdown deadline",
                    "relay.owner_shutdown_timeout",
                )
                raise self._renewal_error
            await asyncio.gather(self._renewal_task, return_exceptions=True)
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
        self._cleanup_complete = True
        if self._renewal_error is not None:
            raise self._renewal_error

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
            self._require_open()
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise RelayTimeoutError(timeout_message, timeout_code)
            try:
                snapshot = await self._control.session(
                    self.session_id,
                    self.credentials.source_token,
                    timeout_seconds=_bounded_request_timeout(
                        remaining,
                        self._request_timeout_seconds,
                    ),
                )
            except ControlPlaneError as error:
                if error.code != "control.request":
                    raise
                await asyncio.sleep(
                    min(poll_interval_seconds, max(0.0, deadline - monotonic()))
                )
                continue
            if predicate(snapshot):
                return snapshot
            await asyncio.sleep(
                min(poll_interval_seconds, max(0.0, deadline - monotonic()))
            )

    def _require_open(self) -> None:
        if self._renewal_error is not None:
            raise self._renewal_error
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
