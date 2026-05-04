# ClauseLens

ClauseLens is an AI due diligence workspace for reviewing contracts and other legal documents. The app is designed as a portfolio-grade full stack system with document ingestion, retrieval, structured analysis, and auditable AI answers.

## Product scope

- Create workspaces for document review
- Upload legal files and track ingestion state
- Generate AI summaries, red flags, obligations, and follow-up questions
- Ask questions over uploaded documents with citations
- Keep an audit trail for uploads, analyses, and chat events

## Monorepo layout

```text
apps/
  web/      Next.js frontend
  api/      FastAPI application
  worker/   Background processing worker
docs/
  architecture.md
infra/
  docker-compose.yml
```

## Planned stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Worker: Celery with Redis
- Worker: DB-backed polling worker for the local MVP
- Data: SQLite by default for local MVP, Postgres and pgvector when configured, local file storage for MVP
- AI: OpenAI for embeddings, structured analysis, and Q&A

## Local development

1. Copy `.env.example` to `.env`.
2. Start infrastructure with Docker Compose.
3. Run `npm install` from the repo root.
4. Create a Python 3.13 environment for backend services:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib python3.13 -m venv .venv313
DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib .venv313/bin/pip install -r apps/api/requirements.txt
```

5. Run the web app, API, and worker in separate terminals:

```bash
npm run dev:web
npm run dev:api
npm run dev:worker
```

The web script includes a `NODE_OPTIONS=--no-experimental-webstorage` runtime fix because the local Node 25 environment exposes a broken server-side `localStorage` object that otherwise causes Next.js dev rendering to fail.

By default the API uses a local SQLite database file at `apps/api/clauselens.db` for a zero-setup demo flow. Set `DATABASE_URL_OVERRIDE` in `.env` if you want to point the backend at Postgres instead.

`PROCESSING_MODE` controls how document ingestion runs:

- `worker` (default): uploads are queued and completed by `npm run dev:worker`
- `inline`: uploads are parsed, embedded, and analyzed inside the API request, which is simpler for single-service deployments

If `OPENAI_API_KEY` is configured, new uploads run through a real OpenAI-backed analysis call using the Responses API plus structured JSON output. If the key is missing or the request fails, ClauseLens falls back to a deterministic local analysis so the demo remains usable offline.

## Current implemented demo flow

- `GET /health`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `GET /api/workspaces/{workspace_id}/audit`
- `GET /api/workspaces/{workspace_id}/documents`
- `GET /api/workspaces/{workspace_id}/chat/history`
- `POST /api/workspaces/{workspace_id}/chat`
- `POST /api/documents/upload`

The current workspace UI now reflects persisted documents, a generated analysis snapshot, and saved chat history from the local database.

Grounded chat answers now pull from persisted document chunks and analysis snapshots, and the assistant returns citation labels that point back to those indexed sources.

Uploads now enter the system in a queued state and are completed by the local worker process when `PROCESSING_MODE=worker`. Run `npm run dev:worker` alongside the API and web app to see documents transition through parsing, chunking, analysis, and final readiness.

When `PROCESSING_MODE=inline`, the same upload endpoint runs parsing, embeddings, and analysis synchronously inside the API. This mode is recommended for simple production deployments where the API and worker do not share a filesystem.

## Production deployment

Recommended production split:

- Frontend: `Vercel`
- Backend API: `Render`
- Database: `Render Postgres`

### Render backend settings

Use a single Python web service for the API.

- Root directory: leave empty
- Build command: `pip install -r apps/api/requirements.txt`
- Start command: `uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port $PORT`

Recommended environment variables:

- `APP_ENV=production`
- `PROCESSING_MODE=inline`
- `DATABASE_URL_OVERRIDE=postgresql+psycopg://...`
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-4o-mini`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `UPLOAD_DIR=./uploads`
- `CORS_ORIGINS=https://your-vercel-domain.vercel.app`

### Vercel frontend settings

- Root directory: `apps/web`
- Build command: `npm run build`
- Output: default Next.js output

Recommended environment variables:

- `NEXT_PUBLIC_API_URL=https://your-render-api.onrender.com`

Detailed setup and architecture notes live in [`docs/architecture.md`](./docs/architecture.md).
