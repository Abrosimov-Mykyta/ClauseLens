import { ChatConsole } from "../../../../components/chat-console";
import { Topbar } from "../../../../components/topbar";
import { getWorkspaceChatHistory, getWorkspaceDocuments } from "../../../../lib/api";
import { requireViewerSession } from "../../../../lib/viewer-session";

type ChatPageProps = {
  params: Promise<{ id: string }>;
};

export default async function WorkspaceChatPage({ params }: ChatPageProps) {
  const viewer = await requireViewerSession();
  const { id } = await params;
  const history = await getWorkspaceChatHistory(id, viewer.accessToken);
  const documents = await getWorkspaceDocuments(id, viewer.accessToken);
  const initialMessages =
    history.length > 0
      ? history
      : [
          {
            id: "demo-user",
            role: "user" as const,
            content: "Which clauses look risky in the supplier agreement?",
            citations: [],
            created_at: new Date().toISOString(),
          },
          {
            id: "demo-assistant",
            role: "assistant" as const,
            content:
              "Three clauses stand out: a broad indemnity obligation, an auto-renewal section with a short cancellation window, and a change-of-control restriction. Each answer should later cite supporting chunks from the indexed documents.",
            citations: ["supplier-agreement.pdf#section-4", "supplier-agreement.pdf#section-9"],
            created_at: new Date().toISOString(),
          },
        ];

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

      <ChatConsole workspaceId={id} initialMessages={initialMessages} documents={documents} />
    </main>
  );
}
