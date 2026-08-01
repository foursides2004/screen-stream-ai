# Local Client — Python Screen Capture Agent

## Tech Stack
- **Runtime**: Python 3.11+ (Windows and macOS)
- **Screen Capture**: `mss` (cross-platform) for high-performance screen capture
- **Image Encoding**: `Pillow` (PIL) for JPEG/WebP encoding
- **Networking**: `requests` for HTTP
- **Hotkeys**: `pynput` for global keyboard listener (cross-platform)
- **Window Capture**: `pygetwindow` (Windows) or `pyobjc-framework-Quartz` (macOS)
- **Packaging**: `pip install -r requirements.txt`

## Key Files
- `capture_agent.py` — Main capture agent with Config, ScreenCapture, APIClient, HotkeyManager, CaptureAgent classes
- `platform_utils.py` — Cross-platform window enumeration (Windows: pygetwindow, macOS: Quartz)
- `reviewer_databank.py` — Local JSON Q&A storage
- `parse_response.py` — Parse structured Q&A from Gemini responses
- `requirements.txt` — Python dependencies (platform-conditional)
- `config.json` — Runtime configuration (gitignored, auto-created with defaults)

## Platform Support

| Feature | Windows | macOS |
|---------|---------|-------|
| Screen capture | ✅ `mss` | ✅ `mss` (needs Screen Recording permission) |
| Hotkeys | ✅ `pynput` | ✅ `pynput` (needs Accessibility permission) |
| Window capture | ✅ `pygetwindow` | ✅ `pyobjc-framework-Quartz` |
| Image encoding | ✅ Pillow | ✅ Pillow |

## Configuration
- `config.json` contains runtime settings including `secretKey`, `apiBaseUrl`, `captureMode`, etc.
- Hotkey defaults are platform-aware (Ctrl+Alt on Windows, Cmd+Shift on macOS)
- Default capture interval: 30 seconds
- Default image format: WebP

## Hotkeys

### Windows
- `Ctrl+Alt+S` — Manual capture
- `Ctrl+Alt+A` — Toggle auto-capture
- `Ctrl+Alt+M` — Cycle capture mode (monitor/window)
- `Ctrl+Alt+Q` — Quit

### macOS
- `Cmd+Shift+S` — Manual capture
- `Cmd+Shift+A` — Toggle auto-capture
- `Cmd+Shift+M` — Cycle capture mode (monitor/window)
- `Cmd+Shift+Q` — Quit

## macOS Permissions
- **Accessibility**: System Settings → Privacy & Security → Accessibility → add Terminal/Python
- **Screen Recording**: System Settings → Privacy & Security → Screen Recording → add Terminal/Python
- **Xcode CLI Tools**: `xcode-select --install` (for window capture)

## Development
- Edit `config.json` to change settings (restart agent after changes)
- Agent runs in foreground with keyboard interrupt support
- Run with `python capture_agent.py` or `python capture_agent.py --domain AWS`
