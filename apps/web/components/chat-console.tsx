"use client";

import { useState, useTransition } from "react";

import { askWorkspaceQuestion, type ChatHistoryMessage } from "../lib/api";

type ChatConsoleProps = {
  workspaceId: string;
  initialMessages: ChatHistoryMessage[];
};

export function ChatConsole({ workspaceId, initialMessages }: ChatConsoleProps) {
  const [messages, setMessages] = useState<ChatHistoryMessage[]>(initialMessages);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <div className="list">
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className="list-item">
            <strong>{message.role === "user" ? "Reviewer" : "ClauseLens AI"}</strong>
            <p className="lede">{message.content}</p>
            {message.citations?.length ? (
              <p className="helper-text">Citations: {message.citations.join(" • ")}</p>
            ) : null}
          </article>
        ))}
      </div>

      <div className="composer">
        <textarea
          className="composer-input"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about risks, obligations, unusual clauses, or missing protections..."
          rows={4}
        />
        <div className="cta-row">
          <button
            type="button"
            className="button button-primary"
            disabled={!question.trim() || isPending}
            onClick={() => {
              const trimmed = question.trim();
              if (!trimmed) {
                return;
              }

              const optimisticQuestion: ChatHistoryMessage = {
                id: `optimistic-${Date.now()}`,
                role: "user",
                content: trimmed,
                citations: [],
                created_at: new Date().toISOString(),
              };

              setMessages((current) => [...current, optimisticQuestion]);
              setQuestion("");
              setError(null);

              startTransition(async () => {
                try {
                  const response = await askWorkspaceQuestion(workspaceId, trimmed);
                  setMessages((current) => [
                    ...current,
                    {
                      id: `assistant-${Date.now()}`,
                      role: "assistant",
                      content: response.answer,
                      citations: response.citations,
                      created_at: new Date().toISOString(),
                    },
                  ]);
                } catch {
                  setError("Question failed. Check that the API is running and try again.");
                }
              });
            }}
          >
            {isPending ? "Thinking..." : "Ask ClauseLens"}
          </button>
        </div>
        {error ? <p className="error-text">{error}</p> : null}
      </div>
    </section>
  );
}
