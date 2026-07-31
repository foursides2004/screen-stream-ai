# Local Client — Python Screen Capture Agent

## Tech Stack
- **Runtime**: Python 3.11+ on Windows 11
- **Screen Capture**: `mss` (MSS-python) for high-performance screen capture
- **Image Encoding**: `Pillow` (PIL) for JPEG/WebP encoding
- **Networking**: `requests` for HTTP, `websockets` for WebSocket streaming
- **Config**: `pydantic-settings` with `.env` file support
- **Logging**: Structured logging with `print` (simple approach)
- **Async Runtime**: `asyncio` for WebSocket operations
- **Packaging**: `pip install -r requirements.txt`

## Key Files
- `capture_agent.py` — Main capture agent with Config, ScreenCapture, APIClient, HotkeyManager, CaptureAgent classes
- `requirements.txt` — Python dependencies
- `config.json` — Runtime configuration (gitignored, contains secrets)

## Configuration
- `config.json` contains runtime settings including `secretKey`, `apiBaseUrl`, `captureMode`, etc.
- `.env` file for local environment variables (gitignored)
- Default capture interval: 20 seconds
- Default image format: WebP
- Deduplication disabled by default (configurable)

## Hotkeys
- `Ctrl+Alt+S` — Manual capture
- `Ctrl+Alt+A` — Toggle auto-capture
- `Ctrl+Alt+M` — Cycle capture mode (monitor/window)
- `Ctrl+Alt+Q` — Quit

## API Communication
- Sends images as base64 data URLs to `/api/analyze` endpoint
- Requires `secretKey` in request body
- Streams response with retry logic (3 attempts)
- SSE broadcast for real-time dashboard updates

## Development
- Edit `config.json` to change settings (restart agent after changes)
- Agent runs in foreground with keyboard interrupt support
- Window capture requires `pygetwindow` package (optional)
