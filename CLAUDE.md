# Screen Stream AI

A modular, end-to-end screen-reading AI assistant that captures a local display feed and makes streaming AI analysis accessible in real-time via a secure web browser UI. Runs on Gemini API (free tier) or OpenRouter. Monorepo: Next.js web app + lightweight Python client (Windows/macOS).

## Architecture

```
Python Client                         Vercel Backend
─────────────                         ──────────────
1. Capture screen (mss)
   - Window mode: captures client area only (Win32 API, no title bar)
   - Supports wildcard title matching (e.g., "Screenshot" matches all)
2. IF mock=true: use MockResponder
   ELSE IF lensEnabled=true:
     a. Lens OCR extracts text (free, no API key)
     b. OCR quality check: min 100 chars, >40% letters, must have "?" or choice labels
     c. If OCR is garbage → fall back to image mode
     d. RAG: search knowledge base for relevant docs
     e. Send text + RAG context to LLM (text-only, cheap)
   ELSE:
     Encode image to base64
     RAG: search knowledge base for relevant docs
     Call LLM (image + context, most tokens, most accurate)
3. Get response text
4. Parse response for Q&A (parse_qa_from_response)
   - Resolves answer labels (A, B, C) to actual content text
   - Drops unresolved single-letter labels
5. Save to local ReviewerDatabank
6. POST /api/reviewer/entries ─────→  7. Store entry, broadcastToSSE (type: "qa_entry")
8. POST /api/submit ───────────────→  9. BroadcastToSSE (type: "analysis", answers only)
```

**LLM Provider** (configured via `config.json`):
- **`geminiApiKey` set** → Direct Gemini API (free tier, `gemini-3.6-flash` default, 1M context)
- **`geminiApiKey` empty** → OpenRouter (free tier models)
- Gemini uses OpenAI-compatible endpoint at `generativelanguage.googleapis.com/v1beta/openai`

**Three analysis modes** (configured via `config.json`):
- **`mock: true`** — Canned responses, zero API cost
- **`lensEnabled: true`** — Google Lens OCR (free) → LLM text-only (cheap). Avoids image tokens.
- **Default** — Full image to LLM (most tokens, most accurate)

**RAG (Retrieval-Augmented Generation)**: Searches local knowledge base (`knowledge/{domain}/`) for relevant documentation and injects it into the system prompt. Enabled by default (`ragEnabled: true`).

**Answer format**: `correctAnswer` saves actual content text (e.g., `"OrderMgr"`) NOT labels (e.g., `"A"`). The parser resolves labels to content using the choices array. This is critical because answer order may be randomized between sessions.

**Question databank**: Stored in `reviewer_databank.json`. Sync to Vercel is opt-in (`syncToVercel: false` by default).

**Dashboard display**: Shows only the resolved answers (not the question text).

**Window capture**: Uses Win32 API (`GetClientRect`) to capture only the content area, excluding title bar and borders. Falls back to full window + 35px crop when unavailable. Supports wildcard title matching for windows with changing names (e.g., screenshots with timestamps).

## Security & Environment

- **Never commit secrets**: All `.env*` files with real keys are gitignored (`config.json` is gitignored)
- **Local Only**: Python client runs on localhost only, no external exposure

## Code Conventions

### Knowledge Base & RAG Rules
- **NEVER hardcode exam answers** in knowledge base files — only factual documentation (API return types, syntax, definitions)
- **NEVER assume what the correct answer is** — the model reads docs and determines answers itself
- **NEVER add "common exam question" patterns** with predetermined correct answers
- Knowledge base files contain: method signatures, return types, parameter descriptions, syntax examples
- The model uses this factual documentation to reason about answers — we don't guide it

### TypeScript/Next.js
- **Strict TypeScript**: `strict: true`, no `any`, prefer `unknown` and type guards
- **App Router**: Use Server Components by default, Client Components only when needed (`'use client'`)
- **API Routes**: Use `export const runtime = 'edge'` for `/api/chat`, `'nodejs'` for `/api/health` and `/api/analyze`
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

- **Gemini API**: Free tier with `gemini-3.6-flash` (1M context, 15 RPM)
- **OpenRouter**: Free tier models available as fallback
- **Vercel**: Hobby plan (100GB bandwidth, 100GB-hours serverless)
- **Python Client**: Runs locally, no cloud cost
- **Google Lens OCR**: Free, no API key required

## Code Quality Standards

- **TypeScript**: `strict: true`, no `any`, prefer `unknown` and type guards
- **Python**: `mypy --strict` clean, `ruff` for linting
- **Testing**: `vitest` for Next.js, `pytest` for Python (when tests added)
- **Linting**: `eslint` (Next.js config), `ruff` (Python)
- **Formatting**: `prettier` (JS/TS), `ruff format` (Python)
