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
- `src/app/api/chat/route.ts` — Streaming chat completion endpoint
- `src/app/api/health/route.ts` — Health check endpoint
- `src/app/page.tsx` — Main dashboard UI
- `src/app/components/` — React components (ChatInterface, StreamDisplay, ConnectionStatus, SettingsPanel)
- `src/app/lib/openrouter.ts` — OpenRouter SDK wrapper

## API Endpoints

### POST /api/analyze
Sends screen capture images to Gemini for AI analysis. Requires `secretKey` in body. Streams response via SSE broadcast.

### GET /api/stream
SSE endpoint for real-time dashboard updates. Clients connect here to receive analysis results.

### POST /api/chat
Streaming chat completion via OpenRouter. Accepts messages array with optional image_url content.

### GET /api/health
Returns `{ status: "healthy", timestamp, version, openrouter: "connected" }`

## Deployment
- Deployed to Vercel
- Environment variables set in Vercel Dashboard
- `.env.production` not committed (gitignored)
