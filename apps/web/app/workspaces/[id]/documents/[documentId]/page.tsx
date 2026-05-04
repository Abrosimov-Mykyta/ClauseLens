import Link from "next/link";

import { DocumentActions } from "../../../../../components/document-actions";
import { Topbar } from "../../../../../components/topbar";
import { buildCitationAnchor, getWorkspaceDocument } from "../../../../../lib/api";

type DocumentDetailPageProps = {
  params: Promise<{ id: string; documentId: string }>;
};

export default async function DocumentDetailPage({ params }: DocumentDetailPageProps) {
  const { id, documentId } = await params;
  const document = await getWorkspaceDocument(id, documentId);

  return (
    <main className="page-shell">
      <Topbar />

      <section className="panel">
        <div className="eyebrow">Document evidence view</div>
        <h1 className="section-title">{document.filename}</h1>
        <p className="lede">
          Inspect the processed artifact, latest AI output, and the exact source chunks that power
          grounded answers.
        </p>
        <div className="cta-row">
          <div
            className={`status-pill ${
              document.status === "ready"
                ? ""
                : document.status === "failed"
                  ? "status-pill-warn"
                  : "status-pill-neutral"
            }`}
          >
            {document.status}
          </div>
          <div className="status-pill status-pill-neutral">{document.stage}</div>
          {document.mime_type ? <div className="status-pill">{document.mime_type}</div> : null}
        </div>
        <p className="helper-text">
          Added: {document.created_at} · Updated: {document.updated_at}
        </p>
        <div className="cta-row" style={{ marginTop: 20 }}>
          <Link href={`/workspaces/${id}`} className="button button-secondary">
            Back to workspace
          </Link>
          <Link href={`/workspaces/${id}/chat`} className="button button-primary">
            Ask AI about this evidence
          </Link>
        </div>
      </section>

      <section className="workspace-grid" style={{ marginTop: 24 }}>
        <article className="workspace-card">
          <h3>Retrieval diagnostics</h3>
          <ul className="list">
            <li className="list-item">
              <strong>{document.retrieval_metrics.chunk_count}</strong>
              <p className="helper-text">Chunks available for retrieval</p>
            </li>
            <li className="list-item">
              <strong>{document.retrieval_metrics.embedded_chunk_count}</strong>
              <p className="helper-text">Chunks with embeddings</p>
            </li>
            <li className="list-item">
              <strong>{document.retrieval_metrics.latest_citation_count}</strong>
              <p className="helper-text">Citations on the latest assistant answer</p>
            </li>
          </ul>
        </article>

        <article className="workspace-card">
          <h3>Latest analysis</h3>
          {document.analysis_snapshot ? (
            <ul className="list">
              <li className="list-item">
                <strong>Summary</strong>
                <p className="lede">{document.analysis_snapshot.summary}</p>
              </li>
              <li className="list-item">
                <strong>Red flags</strong>
                <p className="lede">{document.analysis_snapshot.red_flags}</p>
              </li>
              <li className="list-item">
                <strong>Obligations</strong>
                <p className="lede">{document.analysis_snapshot.obligations}</p>
              </li>
              <li className="list-item">
                <strong>Follow-up questions</strong>
                <p className="lede">{document.analysis_snapshot.follow_up_questions}</p>
              </li>
            </ul>
          ) : (
            <p className="lede">Analysis is not ready yet for this document. Refresh after the worker finishes.</p>
          )}
        </article>

        <article className="workspace-card">
          <h3>Reviewer notes</h3>
          <ul className="list">
            <li className="list-item">Use the chunk citations below to validate each AI conclusion.</li>
            <li className="list-item">Cross-check clause wording before escalating red flags.</li>
            <li className="list-item">Continue the conversation in AI chat for targeted diligence questions.</li>
          </ul>
        </article>

        <DocumentActions
          workspaceId={id}
          documentId={document.id}
          initialStatus={document.status}
          initialStage={document.stage}
        />
      </section>

      <section className="panel" style={{ marginTop: 24 }}>
        <h2>Source chunks</h2>
        {document.chunks.length ? (
          <ul className="list">
            {document.chunks.map((chunk) => (
              <li
                key={chunk.id}
                id={buildCitationAnchor(chunk.citation_label)}
                className="list-item citation-target"
              >
                <div className="status-row">
                  <strong>{chunk.citation_label}</strong>
                  <span className="status-pill status-pill-neutral">
                    {chunk.token_count ? `${chunk.token_count} tokens` : "token count pending"}
                  </span>
                  <span className="status-pill status-pill-neutral">
                    {chunk.has_embedding ? "embedding ready" : "no embedding"}
                  </span>
                </div>
                <p className="lede">{chunk.content}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="lede">No chunks indexed yet. The worker may still be processing this document.</p>
        )}
      </section>
    </main>
  );
}
