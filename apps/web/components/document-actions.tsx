"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { requeueWorkspaceDocument, type DocumentSummary } from "../lib/api";

type DocumentActionsProps = {
  workspaceId: string;
  documentId: string;
  initialStatus: string;
  initialStage: string;
};

export function DocumentActions({
  workspaceId,
  documentId,
  initialStatus,
  initialStage,
}: DocumentActionsProps) {
  const router = useRouter();
  const [result, setResult] = useState<DocumentSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const activeStatus = result?.status ?? initialStatus;
  const activeStage = result?.stage ?? initialStage;

  useEffect(() => {
    if (activeStatus === "ready" || activeStatus === "failed") {
      return;
    }

    const intervalId = window.setInterval(() => {
      router.refresh();
    }, 2500);

    return () => window.clearInterval(intervalId);
  }, [activeStage, activeStatus, router]);

  return (
    <div className="workspace-card">
      <h3>Pipeline controls</h3>
      <p className="lede">
        Send this artifact back through the ingestion worker when you want a fresh analysis pass.
      </p>
      <div className="status-row">
        <span className="status-pill">{activeStatus}</span>
        <span className="status-pill status-pill-neutral">{activeStage}</span>
      </div>
      <div className="cta-row">
        <button
          type="button"
          className="button button-secondary"
          disabled={isPending}
          onClick={() => {
            startTransition(async () => {
              try {
                const payload = await requeueWorkspaceDocument(workspaceId, documentId);
                setResult(payload);
                setError(null);
                router.refresh();
              } catch {
                setError("Requeue failed. Check that the API and worker are running.");
              }
            });
          }}
        >
          {isPending ? "Requeueing..." : "Re-run analysis"}
        </button>
      </div>
      {result ? (
        <div className="result-box">
          <strong>Document requeued</strong>
          <p className="lede">
            The pipeline reset this file to <strong>{result.status}</strong> and stage{" "}
            <strong>{result.stage}</strong>.
          </p>
        </div>
      ) : null}
      {error ? <p className="error-text">{error}</p> : null}
    </div>
  );
}
