# Prepare and qualify each Python platform

The wheel contains the native PocketStation engine. Python code remains the
same across platforms, while capture permissions and native audio mechanisms
follow the host operating system.

## Supported Python

PocketStation 0.1.1 supports CPython 3.11 and newer through one ABI3 extension
per operating system and architecture. Install the wheel that matches the host;
do not rely on a sibling Rust checkout.

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
maximum measurements from the same frame definition and clock boundary.

The 10 ms profile sets PocketStation's frame cadence. It does not guarantee
sub-10 ms capture-to-Python, network, browser, or acoustic latency. WAN and TURN
remain outside the current release evidence.
