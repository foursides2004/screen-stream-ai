# Screen Stream AI

A modular, end-to-end screen-reading AI assistant that captures a local display feed and makes streaming AI analysis accessible in real-time via a secure web browser UI. Runs entirely on a FREE tier using OpenRouter API routing. Monorepo: Next.js web app + lightweight Python client (Windows/macOS).

## Architecture

```
Python Client                         Vercel Backend
─────────────                         ──────────────
1. Capture screen (mss)
2. Encode to base64
3. IF mock=true: use MockResponder
   ELSE: call Gemini via OpenRouter ─→ (direct API call, bypasses Vercel)
4. Get response text
5. Parse response for Q&A (parse_qa_from_response)
6. Save to local ReviewerDatabank
7. POST /api/reviewer/entries ─────→  8. Store entry, broadcastToSSE (type: "qa_entry")
9. POST /api/submit ───────────────→  10. BroadcastToSSE (type: "analysis")
```

The Python client calls Gemini directly via OpenRouter (not through Vercel). Vercel serves as the dashboard and reviewer data store. A `mock` flag in `config.json` enables local development without consuming Gemini tokens.

## Security & Environment

- **Never commit secrets**: All `.env*` files with real keys are gitignored
- **OpenRouter Free Tier**: Use free models (e.g., `google/gemini-3.1-flash-lite`)
- **OpenRouter Headers**: Always send `HTTP-Referer` and `X-Title` headers
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
