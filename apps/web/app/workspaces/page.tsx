import { CreateWorkspaceForm } from "../../components/create-workspace-form";
import Link from "next/link";
import { Topbar } from "../../components/topbar";
import { getWorkspaces } from "../../lib/api";

export default async function WorkspacesPage() {
  const workspaces = await getWorkspaces();

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
      </section>

      <section className="workspace-grid" style={{ marginTop: 24 }}>
        <CreateWorkspaceForm />

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
