# ClauseLens Architecture

## Goal

ClauseLens is an AI due diligence workspace that turns uploaded documents into:

- structured summaries
- red flags
- obligations
- follow-up questions
- grounded Q&A with citations

The system is intentionally built as a portfolio-ready full stack product, not just a chat demo.

## High-level architecture

```text
Next.js web app
  -> FastAPI API
     -> SQLAlchemy persistence
     -> local uploads directory (MVP)
     -> OpenAI analysis + embeddings
     -> auth/session ownership layer

Optional local worker
  -> claims queued documents
  -> parses text
  -> chunks content
  -> embeds chunks
  -> writes analysis + retrieval state
```

## Runtime modes

ClauseLens supports two ingestion modes:

### `PROCESSING_MODE=worker`

Used mainly for local architecture demos.

Flow:

1. upload creates a queued document
2. worker claims the queued job
3. worker parses, chunks, embeds, and analyzes
4. workspace and document state become `ready / analyzed`

### `PROCESSING_MODE=inline`

Used for simpler production deployment.

Flow:

1. upload enters the API
2. parsing, chunking, embedding, and analysis run in-request
3. document returns directly as processed state

This avoids shared-filesystem issues between API and worker in single-service deployments such as `Vercel + Render`.

## Core backend domains

### Users

- support `member` and `guest` sessions
- store email, display name, password hash
- own workspaces through `workspace_members`

### Auth sessions

- persisted access tokens
- identify the current viewer on API requests
- allow lightweight auth without introducing JWT infrastructure

### Workspaces

- private containers for diligence reviews
- scoped to the current member or guest
- aggregate documents, analysis, chat, and audit history

### Documents

- uploaded source files
- track lifecycle:
  - `uploaded`
  - `processing`
  - `ready`
  - `failed`

### Document chunks

- parsed text units
- citation labels for evidence linking
- embedding storage for retrieval

### Analysis runs

- structured AI output:
  - summary
  - red flags
  - obligations
  - follow-up questions

### Chat

- workspace-scoped reviewer conversations
- retrieval over document chunks and recent analysis
- citations attached to answers

### Audit logs

- append-only record of:
  - workspace creation
  - uploads
  - analysis lifecycle events
  - reviewer questions

## Retrieval design

ClauseLens uses a lightweight hybrid retrieval approach:

- lexical overlap on the reviewer question
- embedding similarity for document chunks
- recent structured analysis as extra context

The final context bundle can include:

- source document chunks
- analysis `summary`
- analysis `red_flags`
- analysis `obligations`
- analysis `follow_up_questions`

This lets the assistant answer from both raw evidence and recent structured review state.

## Viewer ownership model

After auth was introduced, the app moved away from shared demo data.

Now:

- `GET /api/workspaces` returns only workspaces owned by the current viewer
- workspace detail, document detail, chat history, upload, and requeue actions all resolve through that viewer context
- guest access provisions a private starter workspace instead of dropping users into shared seeded data

This makes the portfolio demo feel much closer to a real SaaS product.

## Main user flows

### Auth flow

1. user registers or logs in
2. or chooses `View as guest`
3. frontend stores a lightweight viewer cookie
4. browser and server-rendered pages pass `Bearer` auth to the API

### Upload flow

1. user uploads a file inside a workspace
2. API persists a document row and audit event
3. document enters `queued` or runs inline immediately
4. parser extracts text
5. chunker creates citation units
6. embeddings are generated
7. analysis snapshot is stored

### Chat flow

1. reviewer asks a question
2. backend retrieves top evidence
3. model answers from retrieved context
4. citations are saved and rendered
5. user can click through into evidence chunks

## Local persistence and production path

### Local MVP

- SQLite for persistence
- local uploads directory
- optional local worker process

### Production MVP

- Postgres via `DATABASE_URL_OVERRIDE`
- inline processing on the API
- Vercel frontend + Render backend

## Known tradeoffs

- uploads are still local-file based instead of object storage
- auth uses simple persisted access tokens instead of a full identity stack
- retrieval is intentionally lightweight rather than a full vector database deployment
- guest sessions are pragmatic product demos, not enterprise access controls

## Why this architecture works well for a portfolio

It shows:

- real backend structure
- clear domain modeling
- async-capable ingestion
- AI integration beyond a single prompt
- evidence-backed answers
- user-scoped ownership
- production deployment thinking and tradeoffs
