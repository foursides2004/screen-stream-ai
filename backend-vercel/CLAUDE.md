# Backend Vercel — Next.js Web App

## Tech Stack
- **Framework**: Next.js 15 (App Router, Turbopack)
- **Runtime**: Node.js 20+ on Vercel Edge/Node runtime
- **Language**: TypeScript 5+ (strict mode, `noUncheckedIndexedAccess: true`)
- **AI SDK**: AI SDK (`ai` package) with OpenAI provider via OpenRouter
- **Streaming**: Native `ReadableStream` + `TextDecoderStream` for SSE
- **Validation**: Zod for request/response validation
- **Styling**: Tailwind CSS 3.4

## API Endpoints

### POST /api/analyze
Sends screen capture images to Gemini for AI analysis. Requires `secretKey` in body. Streams response via SSE broadcast. **Note:** The Python client now calls Gemini directly; this endpoint is kept for backward compatibility.

### POST /api/submit
Accepts pre-computed analysis text from the Python client. Requires `text` and `secretKey` in body. Broadcasts to SSE as `type: "analysis"`. Used when the Python client handles Gemini calls directly (or mock mode).

### GET /api/stream
SSE endpoint for real-time dashboard updates.

### POST /api/reviewer/entries
Stores Q&A entries from the reviewer databank. Broadcasts `type: "qa_entry"` to SSE.
