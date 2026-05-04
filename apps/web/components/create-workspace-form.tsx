"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { createWorkspace } from "../lib/api";

export function CreateWorkspaceForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <article className="workspace-card">
      <h3>Create workspace</h3>
      <p className="lede">
        Start a new diligence review with its own uploads, audit trail, analysis runs, and AI chat context.
      </p>
      <div className="composer">
        <input
          className="composer-input"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Workspace name"
        />
        <textarea
          className="composer-input"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Describe the review scope, deal context, or vendor audit goal..."
          rows={4}
          style={{ marginTop: 12 }}
        />
        <div className="cta-row">
          <button
            type="button"
            className="button button-primary"
            disabled={!name.trim() || description.trim().length < 10 || isPending}
            onClick={() => {
              const trimmedName = name.trim();
              const trimmedDescription = description.trim();
              if (!trimmedName || trimmedDescription.length < 10) {
                return;
              }

              startTransition(async () => {
                try {
                  const workspace = await createWorkspace({
                    name: trimmedName,
                    description: trimmedDescription,
                  });
                  setError(null);
                  router.push(`/workspaces/${workspace.id}`);
                  router.refresh();
                } catch {
                  setError("Workspace creation failed. Check that the API is reachable and try again.");
                }
              });
            }}
          >
            {isPending ? "Creating..." : "Create workspace"}
          </button>
        </div>
        {error ? <p className="error-text">{error}</p> : null}
      </div>
    </article>
  );
}
