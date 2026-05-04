"use client";

import Link from "next/link";
import { Fragment, type ReactNode, useState, useTransition } from "react";

import {
  askWorkspaceQuestion,
  buildCitationAnchor,
  resolveCitationDocument,
  type ChatEvidenceItem,
  type DocumentSummary,
  type ChatHistoryMessage,
} from "../lib/api";

type ChatConsoleProps = {
  workspaceId: string;
  initialMessages: ChatHistoryMessage[];
  documents: DocumentSummary[];
};

function renderMessageContent(content: string): ReactNode {
  const sanitized = content.replace(/\*\*/g, "").trim();
  const blocks = sanitized.split(/\n\s*\n/).filter(Boolean);

  return blocks.map((block, blockIndex) => {
    const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
    const numberedLines = lines.filter((line) => /^\d+\.\s+/.test(line));
    const bulletedLines = lines.filter((line) => /^-\s+/.test(line));

    if (numberedLines.length === lines.length && lines.length > 0) {
      return (
        <ol key={`ordered-${blockIndex}`} className="message-list message-list-ordered">
          {lines.map((line, index) => (
            <li key={`ordered-item-${blockIndex}-${index}`}>
              {line.replace(/^\d+\.\s+/, "")}
            </li>
          ))}
        </ol>
      );
    }

    if (bulletedLines.length === lines.length && lines.length > 0) {
      return (
        <ul key={`bulleted-${blockIndex}`} className="message-list">
          {lines.map((line, index) => (
            <li key={`bulleted-item-${blockIndex}-${index}`}>
              {line.replace(/^-\s+/, "")}
            </li>
          ))}
        </ul>
      );
    }

    return (
      <Fragment key={`paragraph-${blockIndex}`}>
        {lines.map((line, index) => (
          <p key={`paragraph-line-${blockIndex}-${index}`} className="message-paragraph">
            {line}
          </p>
        ))}
      </Fragment>
    );
  });
}

export function ChatConsole({ workspaceId, initialMessages, documents }: ChatConsoleProps) {
  const [messages, setMessages] = useState<ChatHistoryMessage[]>(initialMessages);
  const [latestEvidence, setLatestEvidence] = useState<ChatEvidenceItem[]>([]);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <div className="list">
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className="list-item">
            <strong>{message.role === "user" ? "Reviewer" : "ClauseLens AI"}</strong>
            <div className="message-body">{renderMessageContent(message.content)}</div>
            {message.citations?.length ? (
              <div className="helper-text citation-row">
                <span>Citations:</span>
                <div className="citation-links">
                  {message.citations.map((citation, citationIndex) => {
                    const document = resolveCitationDocument(citation, documents);
                    if (!document) {
                      return (
                        <span key={`${citation}-${citationIndex}`} className="citation-chip">
                          {citation}
                        </span>
                      );
                    }

                    return (
                      <Link
                        key={`${citation}-${citationIndex}`}
                        href={`/workspaces/${workspaceId}/documents/${document.id}#${buildCitationAnchor(citation)}`}
                        className="citation-chip citation-chip-link"
                      >
                        {citation}
                      </Link>
                    );
                  })}
                </div>
              </div>
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
                  setLatestEvidence(response.evidence);
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

      {latestEvidence.length ? (
        <section className="panel" style={{ marginTop: 24 }}>
          <div className="eyebrow">Retrieval preview</div>
          <h3>Evidence used for the latest answer</h3>
          <ul className="list">
            {latestEvidence.map((item, index) => (
              <li key={`${item.citation}-${index}`} className="list-item">
                <strong>{item.label}</strong>
                <p className="helper-text">{item.citation}</p>
                <p className="lede">{item.content_preview}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </section>
  );
}
