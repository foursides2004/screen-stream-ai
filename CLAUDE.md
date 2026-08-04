# Screen Stream AI

Monorepo: Next.js web app (`backend-vercel/`) + Python screen capture client (`local-client/`). Captures screen → Gemini/OpenRouter LLM → real-time dashboard.

## Architecture

See `local-client/CLAUDE.md` for client details, `backend-vercel/CLAUDE.md` for API details.

**Answer format (critical)**: `correctAnswer` stores actual content text (e.g., `"OrderMgr"`), NOT labels (e.g., `"A"`). Parser resolves labels using choices array. Answer order randomizes between sessions.

## Security

- **Never commit secrets**: `.env*` files gitignored; `config.json` gitignored
- **Local Only**: Python client runs on localhost only

## Knowledge Base & RAG Rules
- **NEVER hardcode exam answers** — only factual documentation (API return types, syntax, definitions)
- **NEVER assume what the correct answer is** — the model reads docs and determines answers itself
- **NEVER add "common exam question" patterns** with predetermined correct answers
- Knowledge base files contain: method signatures, return types, parameter descriptions, syntax examples
