# ClauseLens Architecture

## Goal

Build a portfolio-grade AI due diligence workspace that can ingest legal documents, extract structure, surface risk, and answer follow-up questions with citations.

## Architecture overview

```text
Next.js web app
  -> FastAPI application
     -> Postgres for metadata and analysis state
     -> Redis for job orchestration
     -> Local uploads directory for MVP file storage
     -> OpenAI for embeddings and structured analysis
  -> Celery worker
     -> parsing
     -> chunking
     -> embedding
     -> analysis
```

## Core domains

### Workspaces

- Container for a due diligence review
- Holds documents, analysis runs, chat sessions, and audit logs
- Designed to become multi-tenant later with workspace memberships

### Documents

- Source files uploaded by a reviewer
- Track lifecycle states such as `uploaded`, `processing`, `ready`, and `failed`
- Will eventually store parser metadata, MIME types, and ingestion timings

### Analysis

- Structured AI output over a document or workspace
- Summary
- Key obligations
- Red flags
- Follow-up questions

### Chat

- Retrieval-augmented answers over indexed content
- Each answer should include supporting citations
- Full prompt and response traces can later feed audit and eval systems

## Day-one MVP decisions

- Use a monorepo to keep web, API, and worker aligned
- Start with simple demo-backed API responses before wiring the database
- Save uploads locally while keeping the API contract compatible with future object storage
- Build visible dashboard pages early so the project reads well in a portfolio from the first commit

## Planned next steps

1. Add persistent models and migrations
2. Connect upload flow to queued background jobs
3. Implement chunking and embeddings
4. Add structured due diligence analysis prompts
5. Replace demo chat responses with retrieval-backed answers

## Target relational model

- `users`: reviewers and future team members
- `workspaces`: due diligence containers scoped by organization later
- `workspace_members`: role assignments per workspace
- `documents`: uploaded source files and ingestion state
- `document_chunks`: parsed text units with citation labels and future embeddings
- `analysis_runs`: AI-generated summaries, red flags, obligations, and follow-ups
- `chat_sessions`: grouped question-and-answer threads
- `chat_messages`: stored prompts, answers, and citations
- `audit_logs`: append-only operational history for user and system actions
