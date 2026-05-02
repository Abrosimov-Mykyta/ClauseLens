import { ChatConsole } from "../../../../components/chat-console";
import { Topbar } from "../../../../components/topbar";

type ChatPageProps = {
  params: Promise<{ id: string }>;
};

const messages = [
  {
    role: "user" as const,
    content: "Which clauses look risky in the supplier agreement?",
  },
  {
    role: "assistant" as const,
    content:
      "Three clauses stand out: a broad indemnity obligation, an auto-renewal section with a short cancellation window, and a change-of-control restriction. Each answer should later cite supporting chunks from the indexed documents.",
    citations: ["supplier-agreement.pdf#section-4", "supplier-agreement.pdf#section-9"],
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

      <ChatConsole workspaceId={id} initialMessages={messages} />
    </main>
  );
}
