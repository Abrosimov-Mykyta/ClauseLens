import { CreateWorkspaceForm } from "../../components/create-workspace-form";
import Link from "next/link";
import { Topbar } from "../../components/topbar";
import { getWorkspaces } from "../../lib/api";
import { requireViewerSession } from "../../lib/viewer-session";

export default async function WorkspacesPage() {
  const viewer = await requireViewerSession();
  const workspaces = await getWorkspaces(viewer.accessToken);

  return (
    <main className="page-shell">
      <Topbar />
      <section className="panel">
        <div className="eyebrow">Portfolio MVP</div>
        <h1 className="section-title">Workspaces</h1>
        <p className="lede">
          Each workspace groups uploaded documents, asynchronous analysis runs, AI answers, and
          an audit trail.
        </p>
        <div className="viewer-summary">
          <div className={`status-pill ${viewer.mode === "guest" ? "status-pill-neutral" : ""}`}>
            {viewer.mode === "guest" ? "Guest sandbox active" : "Member workspace hub"}
          </div>
          <div className="viewer-meta">
            <span>{viewer.displayName}</span>
            <span>{viewer.email}</span>
          </div>
        </div>
      </section>

      <section className="workspace-grid" style={{ marginTop: 24 }}>
        <CreateWorkspaceForm />

        {workspaces.length === 0 ? (
          <article className="workspace-card">
            <div className="status-pill status-pill-neutral">
              {viewer.mode === "guest" ? "Guest sandbox ready" : "No workspaces yet"}
            </div>
            <h3>{viewer.mode === "guest" ? "Start with your private sandbox" : "Create your first review workspace"}</h3>
            <p className="lede">
              {viewer.mode === "guest"
                ? "Use the create form to open another private review space, or refresh in a moment if your guest sandbox has just been provisioned."
                : "Your account is ready. Create a workspace to start uploading documents, running analysis, and asking grounded follow-up questions."}
            </p>
            <ul className="helper-list">
              <li>Create a workspace with a real review scope or deal name</li>
              <li>Upload one PDF or TXT file to trigger your first analysis snapshot</li>
              <li>Move into chat for cited follow-up questions</li>
            </ul>
          </article>
        ) : null}

        {workspaces.map((workspace) => (
          <article key={workspace.id} className="workspace-card">
            <div className="status-pill">
              {workspace.status === "ready" ? "Ready" : "Processing"}
            </div>
            <h3>{workspace.name}</h3>
            <p className="lede">
              {workspace.documents} documents under review, {workspace.risks} current risks.
            </p>
            <div className="cta-row">
              <Link href={`/workspaces/${workspace.id}`} className="button button-primary">
                Open review
              </Link>
              <Link href={`/workspaces/${workspace.id}/chat`} className="button button-secondary">
                Open chat
              </Link>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
