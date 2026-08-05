# Local Client — Python Screen Capture Agent

## Window Capture
- `captureMode: "window"` — captures specific window by title
- Supports wildcard matching: type `T` at startup, enter `"Screenshot"` to match all screenshots
- Uses Win32 `GetClientRect` to capture content area only (no title bar)
- Falls back to full window + 35px crop when Win32 API unavailable

## Three Analysis Modes

### Mock Mode (`"mock": true`)
- Canned responses, zero API cost

### Lens OCR Mode (`"lensEnabled": true`)
1. Google Lens OCR extracts text (free, no API key)
2. **OCR quality check**: min 100 chars, >40% letter ratio, must contain "?" or choice labels
3. If OCR is garbage → automatically falls back to image mode
4. RAG searches knowledge base for relevant documentation
5. LLM text-only answers from extracted text + RAG context (cheap — no image tokens)

### Full Image Mode (default)
- Sends screenshot as base64 image to LLM (most tokens, most accurate)

## Answer Format
`correctAnswer` saves actual content text (e.g., `"OrderMgr"`) NOT labels (e.g., `"A"`).
Answer order may be randomized between sessions, so content text is always stored.

## Knowledge Base Rules
- **NEVER hardcode exam answers** — only factual documentation
- Knowledge base files: method signatures, return types, parameter descriptions, syntax examples

## Multi-Domain Knowledge Base
Knowledge base lives in `knowledge/<domain>/` as markdown files. Currently supported:
- **SFCC** (`knowledge/sfcc/`): 9 files — API reference, promotions, orders, customers, etc.
- **RPA** (`knowledge/rpa/`): Core concepts, components, tools/platforms
- **Blue Prism** (`knowledge/blueprism/`): Architecture, Process/Object Studio, work queues, credentials
- **JavaScript** (`knowledge/javascript/`): Core JS, Angular, TypeScript, Node.js

Switch domain in `config.json` → `"domain": "SFCC"` / `"RPA"` / `"blueprism"` / `"javascript"`.
The RAG system loads `knowledge/<domain>/` and searches by keyword matching on `##` headers.

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
