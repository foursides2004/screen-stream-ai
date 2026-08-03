# Backend Vercel — Next.js Web App

## Tech Stack
- **Framework**: Next.js 15+ (App Router, Turbopack)
- **Runtime**: Node.js 20+ on Vercel Edge/Node runtime
- **Language**: TypeScript 5+ (strict mode)
- **AI SDK**: AI SDK (`ai` package) with OpenAI provider via OpenRouter
- **Streaming**: Native `ReadableStream` + `TextDecoderStream` for SSE
- **Validation**: Zod for request/response validation
- **Styling**: Tailwind CSS 4+ (CSS-first config)

## Key Files
- `src/app/api/analyze/route.ts` — Main analysis endpoint (sends images to Gemini via OpenRouter)
- `src/app/api/stream/route.ts` — SSE stream endpoint for real-time dashboard updates
- `src/app/page.tsx` — Redirect to `/dashboard`
- `src/app/dashboard/page.tsx` — Main dashboard UI (SSE client, message rendering)
- `src/app/layout.tsx` — Root layout
- `src/app/globals.css` — Global styles and CSS variables

## API Endpoints

### POST /api/analyze
Sends screen capture images to Gemini for AI analysis. Requires `secretKey` in body. Streams response via SSE broadcast. Optional `domain` field adds exam-specific context. **Note:** The Python client now calls Gemini directly; this endpoint is kept for backward compatibility.

### POST /api/submit
Accepts pre-computed analysis text from the Python client. Requires `text` and `secretKey` in body. Broadcasts to SSE as `type: "analysis"` for dashboard display. Used when the Python client handles Gemini calls directly (or mock mode).

### GET /api/stream
SSE endpoint for real-time dashboard updates. Clients connect here to receive analysis results.

### POST /api/reviewer/entries
Stores Q&A entries from the reviewer databank. Accepts `question`, `choices`, `correctAnswer`, `domain`. Broadcasts `type: "qa_entry"` to SSE.

## Deployment
- Deployed to Vercel
- Environment variables set in Vercel Dashboard
- `.env.production` not committed (gitignored)
