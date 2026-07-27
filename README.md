# Screen Stream AI

A modular, end-to-end screen-reading AI assistant that captures a local display feed on Windows and makes the streaming AI analysis accessible in real-time via a secure web browser UI. Runs entirely on the **free tier** using OpenRouter API routing.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MONOREPO STRUCTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  screen-stream-ai/                                              │
│  ├── .gitignore                                                  │
│  ├── package.json                 # Root workspace config        │
│  ├── test-runner.js               # Local batch validation       │
│  ├── CLAUDE.md                    # Project instructions         │
│  │                                                               │
│  ├── backend-vercel/              # Next.js 15+ Web Application  │
│  │   ├── package.json             # Dependencies & scripts       │
│  │   ├── tsconfig.json            # TypeScript config            │
│  │   ├── next.config.ts           # Next.js config               │
│  │   ├── tailwind.config.ts       # Tailwind CSS config          │
│  │   ├── postcss.config.mjs       # PostCSS config               │
│  │   ├── .env.example             # Env template                 │
│  │   ├── .env.local               # Local dev (gitignored)       │
│  │   └── src/                     │
│  │       └── app/                 │
│  │           ├── layout.tsx       # Root layout                  │
│  │           ├── page.tsx         # Redirect to /dashboard       │
│  │           ├── globals.css      # Global styles                │
│  │           ├── dashboard/       │
│  │           │   └── page.tsx     # Live streaming UI            │
│  │           └── api/             │
│  │               ├── analyze/     │
│  │               │   └── route.ts # OpenRouter vision endpoint   │
│  │               └── stream/      │
│  │                   └── route.ts # SSE broadcast endpoint       │
│  │                                                               │
│  └── local-client/                # Python 3 Windows Client      │
│      ├── requirements.txt         # Python deps                  │
│      ├── config.json              # Runtime config               │
│      ├── .env.example             # Env template                 │
│      ├── capture_agent.py         # Main entry point             │
│      └── .env                     # Local secrets (gitignored)   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- **Node.js 20+** and **npm 10+**
- **Python 3.11+** on Windows
- **OpenRouter API key** (free tier at https://openrouter.ai/keys)

### 1. Clone & Install

```bash
git clone <your-repo>
cd screen-stream-ai

# Install root workspace deps
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
cp config.json config.json  # Already exists with defaults
# Edit config.json with your secretKey and monitor index
```

**Required config.json values:**
```json
{
  "secretKey": "your_32_char_secret_matching_backend",
  "monitorIndex": 1,
  "apiBaseUrl": "http://localhost:3000"
}
```

### 3. Run Locally (Development)

**Terminal 1 - Start Next.js:**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 - Start Python Client:**
```bash
npm run dev:client
# Or: cd local-client && python capture_agent.py
```

**Terminal 3 - Open Dashboard:**
Open http://localhost:3000/dashboard in your browser

### 4. Test Screen Capture

Press **`Ctrl+Shift+S`** (default hotkey) on Windows to capture and analyze your screen. The AI response streams live to the dashboard.

Press **`Ctrl+Shift+Q`** to quit the client.

## Local Batch Testing

Run the automated test suite against 50 images in `C:/done`:

```bash
# Ensure Next.js is running on localhost:3000
npm run dev

# In another terminal:
node test-runner.js
```

The test runner:
- Scans `C:/done` for PNG/JPG/WEBP (max 50)
- Downscales to 1920px max width
- POSTs sequentially to `/api/analyze`
- Tracks progress in `test-progress.json` (resumable)
- Logs latency, success/failure rates

## Deployment

### Vercel (Next.js App)

```bash
# Only after local testing passes
cd backend-vercel
vercel --prod
```

Add environment variables in Vercel Dashboard:
- `OPENROUTER_API_KEY`
- `APP_SECRET_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_MODEL`
- `OPENROUTER_REFERER` (your Vercel URL)
- `OPENROUTER_TITLE`
- `NEXT_PUBLIC_APP_URL`
- `NEXT_PUBLIC_API_URL`

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
  "secretKey": "your_app_secret"
}
```

**Response:** Server-Sent Events stream
```
data: {"type":"text","content":"I see..."}
data: {"type":"text","content":" a terminal"}
data: {"type":"done","content":"Full response..."}
```

### GET `/api/stream`
Server-Sent Events endpoint for real-time updates.

**Events:**
- `connected` - Initial connection
- `text` - Streaming token
- `done` - Complete response
- `ping` - Keepalive (30s)

## Configuration

### Backend (`backend-vercel/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `APP_SECRET_KEY` | Yes | Shared secret (32+ chars) |
| `OPENROUTER_MODEL` | No | Default: `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `OPENROUTER_REFERER` | No | Your app URL for OpenRouter |
| `OPENROUTER_TITLE` | No | App name for OpenRouter |

### Local Client (`local-client/config.json`)

| Key | Default | Description |
|-----|---------|-------------|
| `apiBaseUrl` | `http://localhost:3000` | Backend URL |
| `apiEndpoint` | `/api/analyze` | Analysis endpoint |
| `secretKey` | *(required)* | Must match backend |
| `monitorIndex` | `1` | Monitor to capture (0-based) |
| `captureHotkey` | `ctrl+shift+s` | Capture trigger |
| `quitHotkey` | `ctrl+shift+q` | Exit client |
| `maxWidth` | `1920` | Downscale limit |
| `imageQuality` | `80` | WebP/JPEG quality |
| `imageFormat` | `webp` | Output format |
| `requestTimeout` | `30` | API timeout (seconds) |
| `retryAttempts` | `3` | Retry on failure |
| `retryDelay` | `1000` | Retry delay (ms) |

## Project Commands

```bash
# Root workspace
npm run dev           # Start Next.js dev server
npm run dev:client    # Start Python client
npm run dev:all       # Start both concurrently
npm run build         # Build Next.js for production
npm run lint          # Lint all workspaces
npm run install:all   # Install all deps

# Backend
cd backend-vercel && npm run dev       # Dev server (Turbopack)
cd backend-vercel && npm run build     # Production build
cd backend-vercel && npm run type-check # TypeScript check

# Local Client
cd local-client && python capture_agent.py
cd local-client && pip install -r requirements.txt
```

## Free Tier Limits

- **OpenRouter**: Free models only (Nemotron 3 Ultra, Gemini Flash, etc.)
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
- Ensure `mss` has monitor access (Windows: run as admin if needed)
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

MIT License - See LICENSE file for details.