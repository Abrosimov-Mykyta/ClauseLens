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
3. Install dependencies for `apps/web`, `apps/api`, and `apps/worker`.
4. Run the web app, API, and worker in separate terminals.

Detailed setup and architecture notes live in [`docs/architecture.md`](./docs/architecture.md).

