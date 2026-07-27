You are an expert full-stack engineer, DevOps specialist, and systems architect specializing in Next.js 15+, local Node.js environments, the OpenAI SDK Core (adapted for OpenRouter integrations), and Python 3 desktop automation on Windows.

I am building a modular, end-to-end screen-reading AI assistant that captures a local display feed on Windows and makes the streaming AI analysis accessible in real-time via a secure web browser UI. This project runs entirely on a FREE tier using OpenRouter API routing. The application is a monorepo split into two decoupled layers: a Next.js web application and a lightweight Python client running locally on Windows.

## Project Structure

```
screen-stream-ai/
├── CLAUDE.md                    # This file
├── .gitignore
├── package.json                 # Root workspace package.json
├── backend-vercel/              # Next.js 15+ web application (Vercel deployment)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   ├── .env.local               # Local dev (gitignored)
│   ├── .env.production          # Vercel production (gitignored)
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── chat/
   │   │   │   │   └── route.ts    # OpenRouter streaming chat endpoint
   │   │   │   └── health/
   │   │   │       └── route.ts    # Health check endpoint
   │   │   ├── layout.tsx
   │   │   ├── page.tsx            # Main dashboard UI
   │   │   ├── globals.css
   │   │   └── globals.css
   │   │   └── components/
   │   │       ├── ChatInterface.tsx
   │   │       ├── StreamDisplay.tsx
   │   │       ├── ConnectionStatus.tsx
   │   │       └── SettingsPanel.tsx
   │   │   └── lib/
   │   │       ├── openrouter.ts   # OpenRouter SDK wrapper
   │   │       ├── stream.ts       # Streaming utilities
   │   │       └── validation.ts   # Zod schemas
   │   └── public/
   │       └── favicon.ico
└── local-client/                # Python 3 desktop client (Windows)
    ├── requirements.txt
    ├── .env.example
    ├── .env                       # Local only (gitignored)
    ├── main.py                   # Entry point
    ├── capture/
    │   ├── __init__.py
    │   ├── screen.py             # Screen capture (mss/mss-python)
    │   └── encode.py             # JPEG/WebP encoding
    ├── network/
    │   ├── __init__.py
    │   ├── client.py             # HTTP/WebSocket client to Next.js API
    │   └── stream.py             # Streaming upload logic
    ├── config/
    │   ├── __init__.py
    │   └── settings.py           # Pydantic settings from .env
    └── utils/
        ├── __init__.py
        └── logger.py             # Structured logging
```

## Tech Stack

### Next.js Web App (backend-vercel/)
- **Framework**: Next.js 15+ (App Router, Turbopack)
- **Runtime**: Node.js 20+ on Vercel Edge/Node runtime
- **Language**: TypeScript 5+ (strict mode)
- **AI SDK**: OpenAI SDK Core (`openai` npm package) configured for OpenRouter base URL
- **Streaming**: Native `ReadableStream` + `TextDecoderStream` for SSE
- **Validation**: Zod for request/response validation
- **Styling**: Tailwind CSS 4+ (CSS-first config)
- **Deployment**: Vercel (Edge Runtime for `/api/chat`, Node for `/api/health`)
- **Env Management**: `.env.local` (local), Vercel Project Settings (production)

### Python Local Client (local-client/)
- **Runtime**: Python 3.11+ on Windows 11
- **Screen Capture**: `mss` (MSS-python) for high-performance screen capture
- **Image Encoding**: `Pillow` (PIL) for JPEG/WebP encoding, `cv2` (opencv-python) optional for WebP
- **Networking**: `aiohttp` for async HTTP/WebSocket, `websockets` for WebSocket streaming
- **Config**: `pydantic-settings` with `.env` file support
- **Logging**: `structlog` for structured JSON logging
- **Async Runtime**: `asyncio` native
- **Packaging**: `pip install -r requirements.txt` (no packaging needed)

## Environment Variables

### Root `.env.example` (template only, not used directly)
```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_SITE_NAME=ScreenStreamAI

# Python Client
SCREEN_CAPTURE_MONITOR=0
SCREEN_CAPTURE_FPS=5
SCREEN_CAPTURE_QUALITY=75
SCREEN_CAPTURE_FORMAT=jpeg
SCREEN_CAPTURE_MONITOR_INDEX=0

# API Connection
API_BASE_URL=http://localhost:3000
API_CHAT_ENDPOINT=/api/chat
API_WS_ENDPOINT=/api/ws
API_TIMEOUT=30
```

### backend-vercel/.env.local (local dev)
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_SITE_NAME=ScreenStreamAI
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### backend-vercel/.env.production (Vercel Dashboard - NOT in repo)
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=https://your-app.vercel.app
OPENROUTER_SITE_NAME=ScreenStreamAI
NEXT_PUBLIC_API_URL=https://your-app.vercel.app
```

### local-client/.env (local only, gitignored)
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

SCREEN_CAPTURE_MONITOR=0
SCREEN_CAPTURE_FPS=5
SCREEN_CAPTURE_QUALITY=75
SCREEN_CAPTURE_FORMAT=jpeg
SCREEN_CAPTURE_MONITOR_INDEX=0

API_BASE_URL=http://localhost:3000
API_CHAT_ENDPOINT=/api/chat
API_WS_ENDPOINT=/api/ws
API_TIMEOUT=30
```

## API Specification

### POST /api/chat
**Streaming chat completion via OpenRouter (SSE)**

Request:
```json
{
  "messages": [
    {"role": "user", "content": "What's on my screen?"},
    {"role": "assistant", "content": "I see..."},
    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]}
  ],
  "model": "anthropic/claude-3.5-sonnet",
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 2048
}
```

Response: `text/event-stream` (SSE)
```
data: {"choices":[{"delta":{"content":"I see..."}}]}
data: {"choices":[{"delta":{"content":" a desktop"}}]}
data: [DONE]
```

### GET /api/health
**Health check endpoint**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "version": "1.0.0",
  "openrouter": "connected"
}
```

### Python Client → API Flow
1. Capture screen via `mss` at configured FPS/quality
2. Encode to JPEG/WebP base64
3. POST to `/api/chat` with image as `image_url` in user message
3. Stream SSE response, render in local UI or forward to WebSocket

## Development Commands

```bash
# Root workspace
npm install                    # Install root deps (if any)
cd backend-vercel && npm install
cd local-client && pip install -r requirements.txt

# Development
cd backend-vercel && npm run dev       # Next.js dev server (Turbopack)
cd local-client && python main.py      # Python client

# Build
cd backend-vercel && npm run build     # Production build
cd backend-vercel && npm run lint      # Lint

# Deploy
vercel deploy --prod                   # Deploy to Vercel
```

## Code Conventions

### TypeScript/Next.js
- **Strict TypeScript**: `strict: true`, `noUncheckedIndexedAccess: true`
- **App Router**: Use Server Components by default, Client Components only when needed (`'use client'`)
- **API Routes**: Use `export const runtime = 'edge'` for `/api/chat`, `'nodejs'` for `/api/health`
- **Streaming**: Use `OpenAI` SDK with `stream: true`, return `ReadableStream` via `Response`
- **Validation**: Zod schemas for all API inputs/outputs
- **Error Handling**: Return `Response.json({ error: string }, { status })` with proper status codes
- **Env Access**: `process.env.VAR_NAME` (server), `process.env.NEXT_PUBLIC_*` (client)

### Python
- **Type Hints**: Full type hints with `from __future__ import annotations`
- **Settings**: `pydantic-settings.BaseSettings` with `SettingsConfigDict(env_file='.env')`
- **Async**: `async/await` throughout, `asyncio.run(main())` entry point
- **Logging**: `structlog` with JSON output, structured fields
- **Error Handling**: Custom exceptions, `try/except` with structured logging
- **Async HTTP**: `aiohttp.ClientSession` with timeout and retry logic

### Environment & Security
- **Never commit secrets**: All `.env*` files with real keys are gitignored
- **OpenRouter Free Tier**: Use free models (e.g., `anthropic/claude-3.5-sonnet`, `google/gemini-flash-1.5`)
- **OpenRouter Headers**: Always send `HTTP-Referer` and `X-Title` headers
- **Local Only**: Python client runs on Windows localhost only, no external exposure

## Development Workflow

1. **Start Next.js dev server**: `cd backend-vercel && npm run dev` (port 3000)
2. **Configure Python client**: Edit `local-client/.env` with `API_BASE_URL=http://localhost:3000`
3. **Run Python client**: `cd local-client && python main.py`
4. **Open browser**: Navigate to `http://localhost:3000` to view stream
5. **Develop**: Hot reload works for both Next.js (Turbopack) and Python (restart on change)

## Deployment

### Vercel (Next.js App)
1. Push to GitHub
2. Import in Vercel
3. Add environment variables in Vercel Dashboard
4. Deploy

### Python Client (Local Only)
- Runs on Windows machine with screen to capture
- Configure `.env` with production Vercel URL
- Run as background process or scheduled task

## Free Tier Constraints

- **OpenRouter**: Free tier models only (check OpenRouter docs for current free models)
- **Vercel**: Hobby plan (100GB bandwidth, 100GB-hours serverless)
- **Python Client**: Runs locally, no cloud cost
- **Rate Limits**: Respect OpenRouter rate limits (free tier: ~20 req/min)

## Code Quality Standards

- **TypeScript**: `strict: true`, no `any`, prefer `unknown` and type guards
- **Python**: `mypy --strict` clean, `ruff` for linting
- **Testing**: `vitest` for Next.js, `pytest` for Python (when tests added)
- **Linting**: `eslint` (Next.js config), `ruff` (Python)
- **Formatting**: `prettier` (JS/TS), `ruff format` (Python)