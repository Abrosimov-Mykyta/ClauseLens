"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { uploadDocument, type DocumentUploadResult } from "../lib/api";

type UploadPanelProps = {
  workspaceId: string;
  workspaceName: string;
};

export function UploadPanel({ workspaceId, workspaceName }: UploadPanelProps) {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<DocumentUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <div className="workspace-card">
      <h3>Upload documents</h3>
      <p className="lede">
        Send a contract, memo, or diligence file into <strong>{workspaceName}</strong> and queue it
        for parsing and analysis.
      </p>
      <label className="upload-dropzone">
        <span>Select a file for the ingestion queue</span>
        <input
          type="file"
          onChange={(event) => {
            setSelectedFile(event.target.files?.[0] ?? null);
            setResult(null);
            setError(null);
          }}
        />
      </label>
      <div className="cta-row">
        <button
          type="button"
          className="button button-primary"
          disabled={!selectedFile || isPending}
          onClick={() => {
            if (!selectedFile) {
              return;
            }

            startTransition(async () => {
              try {
                const response = await uploadDocument(workspaceId, selectedFile);
                setResult(response);
                setError(null);
                router.refresh();
              } catch {
                setError("Upload failed. Check that the API is running and try again.");
              }
            });
          }}
        >
          {isPending ? "Uploading..." : "Queue upload"}
        </button>
      </div>

      {selectedFile ? <p className="helper-text">Selected: {selectedFile.name}</p> : null}
      {result ? (
        <div className="result-box">
          <strong>Document accepted</strong>
          <p className="lede">
            {result.filename} is now <strong>{result.status}</strong> and marked as{" "}
            <strong>{result.stage}</strong>.
          </p>
        </div>
      ) : null}
      {error ? <p className="error-text">{error}</p> : null}
    </div>
  );
}
