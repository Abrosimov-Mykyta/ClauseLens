import Link from "next/link";
import { Topbar } from "../components/topbar";
import { highlights, workspaces } from "../lib/demo-data";

export default function HomePage() {
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
          <div className="cta-row">
            <Link href="/workspaces" className="button button-primary">
              Open workspaces
            </Link>
            <Link href="/workspaces/ws-acme/chat" className="button button-secondary">
              Preview AI chat
            </Link>
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
        {workspaces.map((workspace) => (
          <Link key={workspace.id} href={`/workspaces/${workspace.id}`} className="workspace-card">
            <div className="status-pill">
              {workspace.status === "ready" ? "Ready for review" : "Processing"}
            </div>
            <h3>{workspace.name}</h3>
            <p className="lede">
              {workspace.documents} documents, {workspace.risks} flagged issues.
            </p>
            <p>{workspace.updatedAt}</p>
          </Link>
        ))}
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

