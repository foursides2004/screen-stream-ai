# Local Client — Python Screen Capture Agent

## Tech Stack
- **Runtime**: Python 3.11+ (Windows and macOS)
- **Screen Capture**: `mss` (cross-platform) for high-performance screen capture
- **Image Encoding**: `Pillow` (PIL) for JPEG/WebP encoding
- **OCR**: `chrome-lens-py` (Google Lens API, free, no API key)
- **Networking**: `requests` for HTTP (Gemini API + Vercel API)
- **Hotkeys**: `pynput` for global keyboard listener (cross-platform)
- **Window Capture**: `pygetwindow` (Windows) or `pyobjc-framework-Quartz` (macOS)
- **Packaging**: `pip install -r requirements.txt`

## Key Files
- `capture_agent.py` — Main capture agent with Config, ScreenCapture, APIClient, HotkeyManager, CaptureAgent classes
- `gemini_client.py` — Gemini API client with `analyze()` (image) and `analyze_text()` (text-only) methods
- `lens_client.py` — Google Lens OCR client (free, no API key — uses chrome-lens-py)
- `rag_search.py` — RAG (Retrieval-Augmented Generation) keyword search over knowledge base
- `mock_responder.py` — Mock response generator for development (returns valid Q&A format)
- `parse_response.py` — Parse structured Q&A, resolve answer labels → content text
- `reviewer_databank.py` — Local JSON Q&A storage with Vercel sync
- `platform_utils.py` — Cross-platform window enumeration (Windows: pygetwindow, macOS: Quartz)
- `knowledge/` — Domain knowledge base for RAG (e.g., `knowledge/sfcc/*.md`)
- `requirements.txt` — Python dependencies (platform-conditional)
- `config.json` — Runtime configuration (gitignored, auto-created with defaults)

## Utility Scripts
- `populate_databank.py` — Batch process screenshots → databank + Vercel sync
- `merge_new_questions.py` — Process new screenshots, detect duplicates/mismatches, merge
- `migrate_answers.py` — One-time migration: resolve answer labels → content text

## Platform Support

| Feature | Windows | macOS |
|---------|---------|-------|
| Screen capture | ✅ `mss` | ✅ `mss` (needs Screen Recording permission) |
| Hotkeys | ✅ `pynput` | ✅ `pynput` (needs Accessibility permission) |
| Window capture | ✅ `pygetwindow` | ✅ `pyobjc-framework-Quartz` |
| Image encoding | ✅ Pillow | ✅ Pillow |
| Lens OCR | ✅ `chrome-lens-py` | ✅ `chrome-lens-py` |

## Configuration
- `config.json` contains runtime settings including `secretKey`, `apiBaseUrl`, `captureMode`, etc.
- Hotkey defaults are platform-aware (Ctrl+Alt on Windows, Cmd+Shift on macOS)
- Default capture interval: 30 seconds
- Default image format: WebP

## Three Analysis Modes

### Mock Mode (`"mock": true`)
- Canned responses, zero API cost
- Returns realistic Q&A responses parseable by `parse_qa_from_response`
- Saves to local `ReviewerDatabank` and syncs to Vercel backend

### Lens OCR Mode (`"lensEnabled": true`)
1. **Google Lens OCR** extracts text from screenshot (free, no API key)
2. **RAG** searches knowledge base for relevant documentation
3. **Gemini text-only** answers from extracted text + RAG context (cheap — no image tokens)

Falls back to image analysis if OCR fails.

### Full Image Mode (default)
- Sends screenshot as base64 image to Gemini via OpenRouter
- Most tokens, most accurate
- RAG context still injected when `ragEnabled: true`

## Answer Format
`correctAnswer` saves actual content text (e.g., `"OrderMgr"`) NOT labels (e.g., `"A"`).
The parser resolves labels to content using the choices array.

## RAG (Retrieval-Augmented Generation)
- Enabled by default (`ragEnabled: true`)
- Searches `knowledge/{domain}/` markdown files by keyword overlap
- Injects top N chunks into the system prompt as reference material
- Knowledge base contains ONLY factual documentation — never hardcoded answers

## Question Databank
- Local JSON storage: `reviewer_databank.json`
- 99 unique SFCC questions (as of 2026-08-03)
- Syncs to Vercel backend on startup
- Tracks seen count, timestamps, domain

## Gemini / OpenRouter Config
```json
{
  "mock": false,
  "lensEnabled": true,
  "ragEnabled": true,
  "ragTopN": 3,
  "openrouterApiKey": "sk-or-v1-...",
  "openrouterModel": "google/gemini-3.5-flash-lite",
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
- Run with `python capture_agent.py` or `python capture_agent.py --domain SFCC`
- Batch process: `python populate_databank.py` or `python merge_new_questions.py`
