import Link from "next/link";
import { Topbar } from "../../../components/topbar";
import { UploadPanel } from "../../../components/upload-panel";
import { getAuditEvents, getWorkspace } from "../../../lib/api";

type WorkspacePageProps = {
  params: Promise<{ id: string }>;
};

export default async function WorkspaceDetailPage({ params }: WorkspacePageProps) {
  const { id } = await params;
  const workspace = await getWorkspace(id);
  const auditEvents = await getAuditEvents(id);

  return (
    <main className="page-shell">
      <Topbar />
      <section className="panel">
        <div className="eyebrow">Workspace detail</div>
        <h1 className="section-title">{workspace.name}</h1>
        <p className="lede">
          {workspace.description}
        </p>
        <div className="cta-row">
          <div className="status-pill">
            {workspace.status === "ready" ? "Ready for review" : "Processing"}
          </div>
          <div className="status-pill">{workspace.members} reviewers</div>
        </div>
      </section>

      <section className="workspace-grid" style={{ marginTop: 24 }}>
        <article className="workspace-card">
          <h3>Document pipeline</h3>
          <ul className="list">
            <li className="list-item">1. Upload file and persist metadata</li>
            <li className="list-item">2. Queue parsing and chunking job</li>
            <li className="list-item">3. Generate embeddings and structured analysis</li>
          </ul>
        </article>

        <UploadPanel workspaceId={id} workspaceName={workspace.name} />

        <article className="workspace-card">
          <h3>Risk outputs</h3>
          {workspace.latest_analysis ? (
            <ul className="list">
              <li className="list-item">
                <strong>Summary</strong>
                <p className="lede">{workspace.latest_analysis.summary}</p>
              </li>
              <li className="list-item">
                <strong>Red flags</strong>
                <p className="lede">{workspace.latest_analysis.red_flags}</p>
              </li>
              <li className="list-item">
                <strong>Obligations</strong>
                <p className="lede">{workspace.latest_analysis.obligations}</p>
              </li>
              <li className="list-item">
                <strong>Follow-up questions</strong>
                <p className="lede">{workspace.latest_analysis.follow_up_questions}</p>
              </li>
            </ul>
          ) : (
            <p className="lede">No analysis snapshot yet. Upload a document to trigger the first run.</p>
          )}
        </article>

        <article className="workspace-card">
          <h3>Recent activity</h3>
          <ul className="list">
            {workspace.recent_activity.map((item) => (
              <li key={item} className="list-item">
                {item}
              </li>
            ))}
          </ul>
        </article>

        <article className="workspace-card">
          <h3>Next interaction</h3>
          <p className="lede">
            Move to the AI chat surface for cited follow-up questions over the indexed corpus.
          </p>
          <Link href={`/workspaces/${id}/chat`} className="button button-primary">
            Continue to chat
          </Link>
        </article>
      </section>

      <section className="panel" style={{ marginTop: 24 }}>
        <h2>Indexed documents</h2>
        {workspace.documents_list.length ? (
          <ul className="list">
            {workspace.documents_list.map((document) => (
              <li key={document.id} className="list-item">
                <strong>{document.filename}</strong>
                <p className="helper-text">
                  Status: {document.status} · Stage: {document.stage} · Added: {document.created_at}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="lede">No documents uploaded yet for this workspace.</p>
        )}
      </section>

      <section className="panel" style={{ marginTop: 24 }}>
        <h2>Audit timeline</h2>
        <ul className="list">
          {auditEvents.map((event) => (
            <li key={event.id} className="list-item">
              <strong>{event.event_type}</strong>
              <p className="lede">{event.message}</p>
              <small>{event.created_at}</small>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
