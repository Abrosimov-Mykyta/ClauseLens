import { Topbar } from "../../../../components/topbar";

type ChatPageProps = {
  params: Promise<{ id: string }>;
};

const messages = [
  {
    role: "user",
    content: "Which clauses look risky in the supplier agreement?",
  },
  {
    role: "assistant",
    content:
      "Three clauses stand out: a broad indemnity obligation, an auto-renewal section with a short cancellation window, and a change-of-control restriction. Each answer should later cite supporting chunks from the indexed documents.",
  },
];

export default async function WorkspaceChatPage({ params }: ChatPageProps) {
  const { id } = await params;

  return (
    <main className="page-shell">
      <Topbar />
      <section className="panel">
        <div className="eyebrow">Cited Q&A</div>
        <h1 className="section-title">AI chat for {id}</h1>
        <p className="lede">
          The chat service will retrieve relevant chunks, ask the LLM for a grounded answer, and
          save the full interaction for auditability.
        </p>
      </section>

      <section className="panel" style={{ marginTop: 24 }}>
        <div className="list">
          {messages.map((message) => (
            <article key={`${message.role}-${message.content.slice(0, 12)}`} className="list-item">
              <strong>{message.role === "user" ? "Reviewer" : "ClauseLens AI"}</strong>
              <p className="lede">{message.content}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

