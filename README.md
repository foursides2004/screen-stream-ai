# Screen Stream AI

A modular, end-to-end screen-reading AI assistant that captures a local display feed on Windows and makes streaming AI analysis accessible in real-time via a secure web browser UI. Runs entirely on the **free tier** using OpenRouter API routing.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MONOREPO STRUCTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  screen-stream-ai/                                              │
│  ├── .gitignore                                                  │
│  ├── package.json                 # Root workspace config        │
│  ├── main.py                      # Python entry point (root)    │
│  ├── test-runner.js               # Local batch validation       │
│  ├── CLAUDE.md                    # Project instructions         │
│  ├── LICENSE                      # MIT License                  │
│  │                                                               │
│  ├── backend-vercel/              # Next.js 15+ Web Application  │
│  │   ├── package.json             # Dependencies & scripts       │
│  │   ├── tsconfig.json            # TypeScript config            │
│  │   ├── next.config.ts           # Next.js config               │
│  │   ├── tailwind.config.ts       # Tailwind CSS config          │
│  │   ├── postcss.config.js        # PostCSS config               │
│  │   ├── vercel.json              # Vercel deployment config     │
│  │   ├── .env.example             # Env template                 │
│  │   └── src/                     │
│  │       └── app/                 │
│  │           ├── layout.tsx       # Root layout                  │
│  │           ├── page.tsx         # Redirect to /dashboard       │
│  │           ├── globals.css      # Global styles                │
│  │           ├── not-found.tsx    # 404 page                     │
│  │           ├── dashboard/       │
│  │           │   └── page.tsx     # Live streaming UI            │
│  │           └── api/             │
│  │               ├── analyze/     │
│  │               │   └── route.ts # OpenRouter vision endpoint   │
│  │               └── stream/      │
│  │                   └── route.ts # SSE broadcast endpoint       │
│  │                                                               │
│  └── local-client/                # Python 3 Cross-Platform Client│
│      ├── requirements.txt         # Python deps                  │
│      ├── main.py                  # Client entry point           │
│      ├── capture_agent.py         # Core capture logic           │
│      ├── .env.example             # Env template                 │
│      └── .gitignore               # Gitignore for client         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Real-time screen analysis** — captures screen and streams AI responses live to the dashboard
- **Multi-monitor support** — select which monitor to capture
- **Window capture** — capture a specific window by title (Windows via `pygetwindow`, macOS via `pyobjc`)
- **Auto-capture** — configurable interval (default: 30s) with hotkey toggle
- **Image deduplication** — perceptual hash (pHash) to skip near-identical captures
- **Domain context** — pass `--domain AWS` or `--domain SFCC` for exam-specific answers
- **Multi-select awareness** — AI prompt instructs model to find ALL correct answers
- **Streaming dashboard** — SSE-based real-time UI with markdown rendering
- **Batch testing** — test-runner for validating against 50+ images

## Quick Start

### Prerequisites
- **Node.js 20+** and **npm 10+**
- **Python 3.11+** (Windows or macOS)
- **OpenRouter API key** (free tier at https://openrouter.ai/keys)

### 1. Clone & Install

```bash
git clone <your-repo>
cd screen-stream-ai

# Install root workspace deps (includes concurrently, canvas)
npm install

# Install Next.js app deps
cd backend-vercel && npm install && cd ..

# Install Python client deps
cd local-client && pip install -r requirements.txt && cd ..
```

### 2. Configure Environment

**Backend (Next.js):**
```bash
cd backend-vercel
cp .env.example .env.local
# Edit .env.local with your OpenRouter API key and secret
```

**Local Client (Python):**
```bash
cd local-client
cp .env.example .env
# Edit .env with your OpenRouter API key
```

The Python client uses `config.json` for runtime settings (created automatically on first run with defaults). Edit it to set your `secretKey`:

```json
{
  "secretKey": "your_32_char_secret_matching_backend",
  "monitorIndex": 1,
  "apiBaseUrl": "http://localhost:3000"
}
```

### 3. Run Locally (Development)

**Terminal 1 — Start Next.js:**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 — Start Python Client:**
```bash
cd local-client && python main.py
# Or from root: npm run dev:client
```

**Terminal 3 — Open Dashboard:**
Open http://localhost:3000/dashboard in your browser

### 4. Test Screen Capture

Press **`Ctrl+Alt+S`** (default hotkey) on Windows to capture and analyze your screen. The AI response streams live to the dashboard.

Press **`Ctrl+Alt+Q`** to quit the client.

## Hotkeys

| Shortcut (Windows) | Shortcut (macOS) | Action |
|---------------------|-------------------|--------|
| `Ctrl+Alt+S` | `Cmd+Shift+S` | Manual screen capture |
| `Ctrl+Alt+A` | `Cmd+Shift+A` | Toggle auto-capture on/off |
| `Ctrl+Alt+M` | `Cmd+Shift+M` | Cycle capture mode (monitor ↔ window) |
| `Ctrl+Alt+Q` | `Cmd+Shift+Q` | Quit the client |

All hotkeys are configurable in `config.json`. Defaults are set automatically based on your platform.

### macOS Permissions

On macOS, the following permissions are required:

1. **Accessibility** — for global hotkeys (`pynput`)
   - System Settings → Privacy & Security → Accessibility → add Terminal or your Python app
2. **Screen Recording** — for screen capture (`mss`)
   - System Settings → Privacy & Security → Screen Recording → add Terminal or your Python app
3. **Xcode CLI Tools** — for window capture (`pyobjc`)
   - Run `xcode-select --install` if not already installed

## Local Batch Testing

Run the automated test suite against images in `C:/done` (Windows only):

```bash
# Install canvas dependency (Windows only, requires pkg-config + pixman)
npm install canvas

# Ensure Next.js is running on localhost:3000
npm run dev

# In another terminal:
node test-runner.js
```

> **Note:** `test-runner.js` requires the `canvas` npm package (native addon) which needs system-level `pkg-config` and `pixman` libraries. On macOS/Linux, install them via `brew install pkg-config pixman` or `apt install pkg-config libpixman-1-dev`.

The test runner:
- Scans `C:/done` for PNG/JPG/WEBP (max 50)
- Downscales to 1920px max width
- POSTs sequentially to `/api/analyze`
- Tracks progress in `test-progress.json` (resumable)
- Logs latency, success/failure rates

## Deployment

### Vercel (Next.js App)

```bash
cd backend-vercel
vercel --prod
```

Add environment variables in Vercel Dashboard:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `APP_SECRET_KEY` | Yes | Shared secret (32+ chars), generate with `openssl rand -hex 32` |
| `OPENROUTER_BASE_URL` | No | Default: `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | No | Default: `google/gemini-2.0-flash-exp:free` |
| `OPENROUTER_REFERER` | No | Your Vercel app URL |
| `OPENROUTER_TITLE` | No | App name for OpenRouter |
| `NEXT_PUBLIC_APP_URL` | No | Public app URL |
| `NEXT_PUBLIC_API_URL` | No | Public API URL |

### Python Client (Production)

Configure `config.json` with production URL:
```json
{
  "apiBaseUrl": "https://your-app.vercel.app",
  "secretKey": "same_as_vercel_env"
}
```

Run as background service or scheduled task on Windows.

## API Endpoints

### POST `/api/analyze`
Analyzes a screen capture via OpenRouter vision model.

**Request:**
```json
{
  "image": "data:image/webp;base64,...",
  "secretKey": "your_app_secret",
  "domain": "AWS"
}
```

**Response:** Server-Sent Events stream
```
data: {"type":"text","content":"I see..."}
data: {"type":"text","content":" a terminal"}
data: {"type":"done","content":"Full response..."}
```

The `domain` field is optional — when provided, it adds exam-specific context to the AI prompt (e.g., "This is an official AWS exam...").

### GET `/api/stream`
Server-Sent Events endpoint for real-time dashboard updates.

**Events:**
- `connected` — Initial connection
- `analysis` — Complete analysis result
- `ping` — Keepalive (30s)
- `error` — Error message

## Configuration

### Backend (`backend-vercel/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `APP_SECRET_KEY` | Yes | Shared secret (32+ chars) |
| `OPENROUTER_MODEL` | No | Default: `google/gemini-2.0-flash-exp:free` |
| `OPENROUTER_REFERER` | No | Your app URL for OpenRouter |
| `OPENROUTER_TITLE` | No | App name for OpenRouter |

### Local Client (`local-client/config.json`)

| Key | Default | Description |
|-----|---------|-------------|
| `apiBaseUrl` | `http://localhost:3000` | Backend URL |
| `apiEndpoint` | `/api/analyze` | Analysis endpoint |
| `secretKey` | *(required)* | Must match backend |
| `domain` | *(empty)* | Domain context for exam questions (e.g., `AWS`, `SFCC`) |
| `monitorIndex` | `1` | Monitor to capture (0-based) |
| `captureHotkey` | `ctrl+alt+s` | Capture trigger |
| `quitHotkey` | `ctrl+alt+q` | Exit client |
| `toggleAutoCaptureHotkey` | `ctrl+alt+a` | Toggle auto-capture |
| `cycleModeHotkey` | `ctrl+alt+m` | Cycle monitor/window mode |
| `maxWidth` | `1920` | Downscale limit |
| `imageQuality` | `80` | WebP/JPEG quality |
| `imageFormat` | `webp` | Output format |
| `requestTimeout` | `30` | API timeout (seconds) |
| `retryAttempts` | `3` | Retry on failure |
| `retryDelay` | `1000` | Retry delay (ms) |
| `captureInterval` | `30` | Auto-capture interval (seconds) |
| `autoCapture` | `true` | Enable auto-capture on startup |
| `captureMode` | `monitor` | `monitor` or `window` |
| `targetWindowTitle` | *(empty)* | Window title for window capture mode |
| `deduplicationEnabled` | `false` | Skip near-identical images |
| `deduplicationThreshold` | `0.95` | pHash similarity threshold (0-1) |

## Project Commands

```bash
# Root workspace
npm run dev           # Start Next.js dev server
npm run dev:client    # Start Python client
npm run dev:all       # Start both concurrently
npm run build         # Build Next.js for production
npm run lint          # Lint all workspaces
npm run install:all   # Install all deps (npm + pip)

# Backend
cd backend-vercel && npm run dev          # Dev server
cd backend-vercel && npm run build        # Production build
cd backend-vercel && npm run type-check   # TypeScript check

# Local Client
cd local-client && python main.py                      # Run client
cd local-client && python main.py --domain AWS         # Run with domain context
cd local-client && pip install -r requirements.txt     # Install Python deps
```

## Free Tier Limits

- **OpenRouter**: Free models only (Gemini Flash, etc.)
- **Rate Limits**: ~20 requests/minute on free tier
- **Vercel Hobby**: 100GB bandwidth, 100GB-hours serverless
- **Local Client**: No cloud costs, runs on your Windows machine

## Security

- All secrets in `.env.local` / `.env` (gitignored)
- `APP_SECRET_KEY` validates API requests
- OpenRouter requires `HTTP-Referer` and `X-Title` headers
- Local client only connects to configured API URL
- No telemetry or external tracking

## Troubleshooting

**Python client can't capture screen:**
- **macOS**: Grant Screen Recording permission (System Settings → Privacy & Security → Screen Recording)
- **Windows**: Run as admin if needed
- Check `monitorIndex` in config.json (0 = primary, 1 = second, etc.)

**API returns 401 Unauthorized:**
- Verify `secretKey` in config.json matches `APP_SECRET_KEY` in .env.local
- Check both are 32+ character strings

**SSE stream doesn't connect:**
- Check browser console for CORS errors
- Verify Next.js dev server runs on port 3000
- Ensure `NEXT_PUBLIC_API_URL` matches

**Images too large / timeout:**
- Reduce `maxWidth` in config.json
- Lower `imageQuality` (60-80 for WebP)
- Increase `requestTimeout`

## License

MIT License — See [LICENSE](LICENSE) file for details.
