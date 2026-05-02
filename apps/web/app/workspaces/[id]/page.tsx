import Link from "next/link";
import { Topbar } from "../../../components/topbar";

type WorkspacePageProps = {
  params: Promise<{ id: string }>;
};

export default async function WorkspaceDetailPage({ params }: WorkspacePageProps) {
  const { id } = await params;

  return (
    <main className="page-shell">
      <Topbar />
      <section className="panel">
        <div className="eyebrow">Workspace detail</div>
        <h1 className="section-title">Review workspace: {id}</h1>
        <p className="lede">
          This screen will host uploads, ingestion status, extracted findings, and the workspace
          audit stream. For today, we are laying down the page contract and design shell so the
          API can plug in cleanly.
        </p>
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

        <article className="workspace-card">
          <h3>Risk outputs</h3>
          <ul className="list">
            <li className="list-item">Executive summary</li>
            <li className="list-item">Red flags and unusual clauses</li>
            <li className="list-item">Obligations and follow-up questions</li>
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
    </main>
  );
}

