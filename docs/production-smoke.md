# Production Smoke Checklist

Use this checklist after a deploy on `Vercel + Render`.

## Backend

1. Open `/health`
2. Confirm it returns:

```json
{"status":"ok"}
```

3. Confirm `OPENAI_API_KEY`, `DATABASE_URL_OVERRIDE`, and `CORS_ORIGINS` are set
4. Confirm `PROCESSING_MODE=inline` for the single-service production setup

## Frontend

1. Open the deployed homepage
2. Confirm the auth page loads
3. Confirm `NEXT_PUBLIC_API_URL` points at the Render backend

## Auth

1. Register a new member account
2. Sign out
3. Sign back in with the same account
4. Use `View as guest`
5. Confirm guest lands in a private sandbox

## Workspace ownership

1. Member creates a workspace
2. Guest session should not see the member workspace
3. Member should not see the guest sandbox unless using that guest session

## Upload and analysis

1. Upload a `.txt` or text-based `.pdf`
2. Confirm document status moves to `ready / analyzed`
3. Confirm retrieval metrics increase:
   - indexed documents
   - indexed chunks
   - embedded chunks
   - analysis runs

## Chat and citations

1. Ask a grounded question such as:
   - `What looks risky here?`
   - `What obligations should counsel review?`
2. Confirm the answer contains citations
3. Click a citation
4. Confirm it opens the evidence view and scrolls to the cited chunk

## Logout

1. Sign out
2. Confirm workspace pages redirect back to `/auth`

## Known production expectations

- `guest` creates a private starter workspace
- uploads are processed inline in production
- answers may fall back to deterministic local analysis if OpenAI fails
- `404 /favicon.ico` is harmless if it appears in logs
