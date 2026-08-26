# PocketStation Python SDK

Use Python to connect to a PocketStation control plane and Relay, receive PCM
audio, and send application-owned PCM back over the same session.

> **Status: preview.** This repository does not have a PyPI release. The API in
> `main` may change while the native PocketStation Session binding is completed.

## Develop locally

You need Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
```

The current package uses HTTP for session creation and a WebSocket for binary
PCM. Configure the control-plane and Relay URLs in your application; the SDK
does not start hidden infrastructure or select a hosted service for you.

## Related projects

- [PocketStation Core](https://github.com/pocketstation-io/pocketstation)
- [PocketStation Relay](https://github.com/pocketstation-io/relay)
- [PocketStation Control Plane](https://github.com/pocketstation-io/control-plane)
