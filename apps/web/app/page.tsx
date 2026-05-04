import Link from "next/link";
import { Topbar } from "../components/topbar";
import { getWorkspaces } from "../lib/api";
import { highlights } from "../lib/demo-data";
import { getViewerSession } from "../lib/viewer-session";

export default async function HomePage() {
  const viewer = await getViewerSession();
  const workspaces = viewer ? await getWorkspaces(viewer.accessToken) : await getWorkspaces();

  return (
    <main className="page-shell">
      <Topbar />
      <section className="hero">
        <div className="panel">
          <div className="eyebrow">AI Due Diligence Workspace</div>
          <h1 className="headline">Review contracts with structured AI, not guesswork.</h1>
          <p className="lede">
            ClauseLens turns uploaded documents into a searchable risk map with summaries,
            obligations, red flags, and cited answers. The architecture is built to grow from
            a fast MVP into a serious multi-tenant review platform.
          </p>
          {viewer ? (
            <div className="viewer-summary">
              <div className="status-pill status-pill-neutral">
                {viewer.mode === "guest" ? "Guest session active" : "Signed in"}
              </div>
              <div className="viewer-meta">
                <span>{viewer.displayName}</span>
                <span>{viewer.email}</span>
              </div>
            </div>
          ) : null}
          <div className="cta-row">
            {viewer ? (
              <>
                <Link href="/workspaces" className="button button-primary">
                  Open workspaces
                </Link>
                <Link href="/auth" className="button button-secondary">
                  Switch account
                </Link>
              </>
            ) : (
              <>
                <Link href="/auth" className="button button-primary">
                  Login or register
                </Link>
                <Link href="/auth" className="button button-secondary">
                  View as guest
                </Link>
              </>
            )}
          </div>
        </div>

        <aside className="panel">
          <div className="status-pill">System online</div>
          <div className="metrics">
            <div className="metric">
              <div className="metric-label">Workspaces</div>
              <div className="metric-value">03</div>
            </div>
            <div className="metric">
              <div className="metric-label">Documents indexed</div>
              <div className="metric-value">28</div>
            </div>
            <div className="metric">
              <div className="metric-label">Red flags</div>
              <div className="metric-value">12</div>
            </div>
            <div className="metric">
              <div className="metric-label">Audit events</div>
              <div className="metric-value">147</div>
            </div>
          </div>
        </aside>
      </section>

      <h2 className="section-title">Latest workspaces</h2>
      <section className="workspace-grid">
        {workspaces.length ? (
          workspaces.map((workspace) => (
            <Link key={workspace.id} href={`/workspaces/${workspace.id}`} className="workspace-card">
              <div className="status-pill">
                {workspace.status === "ready" ? "Ready for review" : "Processing"}
              </div>
              <h3>{workspace.name}</h3>
              <p className="lede">
                {workspace.documents} documents, {workspace.risks} flagged issues.
              </p>
            </Link>
          ))
        ) : (
          <article className="workspace-card empty-state">
            <h3 className="empty-state-title">No workspaces yet</h3>
            <p className="empty-state-text">
              Start with guest access for a disposable sandbox, or create a member account and open
              your first diligence review workspace.
            </p>
            <div className="cta-row" style={{ marginTop: 0 }}>
              <Link href="/auth" className="button button-primary">
                Open auth
              </Link>
            </div>
          </article>
        )}
      </section>

      <h2 className="section-title">What the AI is surfacing</h2>
      <section className="panel">
        <ul className="list">
          {highlights.map((item) => (
            <li key={item} className="list-item">
              {item}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
