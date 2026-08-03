# Local Client — Python Screen Capture Agent

## Tech Stack
- **Runtime**: Python 3.11+ (Windows and macOS)
- **Screen Capture**: `mss` (cross-platform) for high-performance screen capture
- **Image Encoding**: `Pillow` (PIL) for JPEG/WebP encoding
- **Networking**: `requests` for HTTP (Gemini API + Vercel API)
- **Hotkeys**: `pynput` for global keyboard listener (cross-platform)
- **Window Capture**: `pygetwindow` (Windows) or `pyobjc-framework-Quartz` (macOS)
- **Packaging**: `pip install -r requirements.txt`

## Key Files
- `capture_agent.py` — Main capture agent with Config, ScreenCapture, APIClient, HotkeyManager, CaptureAgent classes
- `gemini_client.py` — Gemini API client (calls OpenRouter directly, same prompt as Vercel backend)
- `lens_client.py` — Google Lens OCR client (free, no API key — uses chrome-lens-py)
- `mock_responder.py` — Mock response generator for development (returns valid Q&A format)
- `platform_utils.py` — Cross-platform window enumeration (Windows: pygetwindow, macOS: Quartz)
- `reviewer_databank.py` — Local JSON Q&A storage
- `parse_response.py` — Parse structured Q&A from Gemini responses
- `rag_search.py` — RAG (Retrieval-Augmented Generation) search over knowledge base
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

## Mock Mode
Set `"mock": true` in `config.json` to skip Gemini API calls and use canned responses. This:
- Returns realistic Q&A responses (parseable by `parse_qa_from_response`)
- Saves to local `ReviewerDatabank` and syncs to Vercel backend
- Submits to Vercel for dashboard display (via `/api/submit`)
- Consumes zero Gemini tokens

When `mock: false`, the Python client calls Gemini directly via OpenRouter. Requires `openrouterApiKey` in `config.json`.

## Lens OCR Mode (Free, No API Key)
Set `"lensEnabled": true` in `config.json` to use the Lens pipeline:
1. **Google Lens OCR** extracts text from screenshot (free, no API key)
2. **Gemini text-only** answers the question from extracted text (cheap — no image tokens)

This is much cheaper than sending images to Gemini because:
- Google Lens OCR uses their full search index (very accurate)
- Text-only Gemini prompts use far fewer tokens than image prompts
- Falls back to image analysis if OCR fails

```json
{
  "lensEnabled": true,
  "mock": false
}
```

## Gemini / OpenRouter Config
```json
{
  "mock": false,
  "lensEnabled": true,
  "openrouterApiKey": "sk-or-v1-...",
  "openrouterModel": "google/gemini-3.1-flash-lite",
  "openrouterBaseUrl": "https://openrouter.ai/api/v1"
}
```

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
