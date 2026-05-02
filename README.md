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
- Data: Postgres, pgvector, local file storage for MVP
- AI: OpenAI for embeddings, structured analysis, and Q&A

## Local development

1. Copy `.env.example` to `.env`.
2. Start infrastructure with Docker Compose.
3. Run `npm install` from the repo root.
4. Create a Python 3.13 environment for backend services:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib python3.13 -m venv .venv313
DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib .venv313/bin/pip install -r apps/api/requirements.txt
DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib .venv313/bin/pip install -r apps/worker/requirements.txt
```

5. Run the web app, API, and worker in separate terminals:

```bash
npm run dev:web
npm run dev:api
npm run dev:worker
```

## Current implemented demo flow

- `GET /health`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `GET /api/workspaces/{workspace_id}/audit`
- `POST /api/workspaces/{workspace_id}/chat`
- `POST /api/documents/upload`

Detailed setup and architecture notes live in [`docs/architecture.md`](./docs/architecture.md).
