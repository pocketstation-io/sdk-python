# Prepare and qualify each Python platform

The wheel contains the native PocketStation engine. Python code remains the
same across platforms, while capture permissions and native audio mechanisms
follow the host operating system.

## Supported Python

PocketStation 0.1.2 supports CPython 3.11 and newer through one ABI3 extension
per operating system and architecture. Install the wheel that matches the host;
do not rely on a sibling Rust checkout.

## Check permission without prompting

`pocketstation.microphone_permission_observation()` reads the current state
without showing consent UI:

```python
import pocketstation as pks

permission = pks.microphone_permission_observation()
print(permission.value)
```

`DENIED`, `RESTRICTED`, and `REVOKED` require a host or user action.
`NOT_DETERMINED` means the host has not decided. `NOT_OBSERVABLE` means the
platform cannot provide an authoritative preflight result; it must not be
treated as approval.

PocketStation does not prompt on import or discovery. Start capture from a
clear user action so the operating system can present consent when supported.
Opening the Source is authoritative and returns a typed failure when capture
cannot start. Application capture and microphone capture use separate
permissions, so enable the microphone only when the workflow needs it.

## Persist a source at its supported scope

Use discovery when the application needs to remember a selection or reopen it
after a restart:

```python
import pocketstation as pks

matches = pks.discover_sources(pks.SourceQuery.application("Zoom"))
if len(matches) != 1:
    raise RuntimeError("Select one running Zoom source")

discovered = matches[0]
source = pks.Source.from_discovered(discovered)
print(discovered.selector_persistence_scope)
```

`Source.from_discovered()` chooses the strongest supported declaration: an
exact process instance plus stable application identity when both exist, a
stable application identity when no process is available, or a native
microphone device ID.

Persist the platform, source kind, stable key, and persistence scope only when
the scope matches the workflow:

| Persistence scope | Safe reuse |
|---|---|
| `APPLICATION_IDENTITY` | Reopen the application identity after a normal restart, then verify discovery still resolves it. |
| `DEVICE_IDENTITY` | Reopen the same installed and permitted device. |
| `PLATFORM_IDENTITY` | Reuse the platform-owned identity on that platform. |
| `PROCESS_LIFETIME` | Reuse only while the exact process is alive. Rediscover after exit. |
| `SESSION_DEFAULT_DEVICE` | Follow the host default on each new Session; do not treat it as a pinned device. |
| `None` | Do not persist the selector. Rediscover before the next Session. |

`source_id` belongs to media lineage. It is not a portable account identifier
or a substitute for the discovered stable key.

## Recover without selecting the wrong source

PocketStation does not switch Sources silently. A source disappearance or
backend failure appears in the Session event stream. When
`recovery_requirement` is
`EXPLICIT_REDISCOVERY_AND_NEW_SESSION`, stop or cancel the current Session,
discover again, let the user confirm any changed selection, and create a new
Session.

Choose fallback behavior explicitly:

- prefer a stored application identity, then require user confirmation before
  falling back to a unique display-name result;
- use `Source.microphone_id()` to pin one device or
  `Source.microphone_default()` to follow the host default on each Session;
- reject zero or multiple discovery matches;
- use separate Connector objects for primary and backup destinations so their
  queues, failures, and shutdown outcomes remain independent; and
- keep provider retries and reconnect attempts finite. The advanced Connector
  API reports readiness, health, and recovery but does not invent a provider
  retry policy.

## macOS

Application capture needs screen and system-audio recording permission.
Microphone capture needs microphone permission. Restart the application after
changing consent when macOS does not update the running process.

The release evidence includes an Apple-silicon installed wheel using a physical
microphone, the 10 ms voice profile, Relay, Chromium, and three recordings.

## Windows

The release workflow builds Windows x64 and ARM64 wheels. Core selector and
10 ms correctness have been exercised in Windows 11 ARM64. VM scheduling is
not a physical-device latency result.

## Linux

The release workflow builds manylinux x86_64 and ARM64 wheels. Application
capture requires access to the logged-in PipeWire session. Microphone capture
uses ALSA. A service or container must receive those devices and session
permissions explicitly.

## Separate correctness from performance

An installed import and component test establish package correctness. A device
claim needs the physical device. A latency claim needs p50, p95, p99, and
maximum measurements from the same frame definition and clock domain.

The 10 ms profile sets PocketStation's frame cadence. It does not guarantee
sub-10 ms capture-to-Python, network, browser, or acoustic latency. WAN and TURN
remain outside the current release evidence.
