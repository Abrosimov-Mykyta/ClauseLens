import { workspaces as demoWorkspaces } from "./demo-data";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type WorkspaceSummary = {
  id: string;
  name: string;
  status: string;
  documents: number;
  risks: number;
};

export type WorkspaceDetail = WorkspaceSummary & {
  description: string;
  members: number;
  recent_activity: string[];
  documents_list: DocumentSummary[];
  latest_analysis: AnalysisSnapshot | null;
};

export type AuditEvent = {
  id: string;
  event_type: string;
  message: string;
  created_at: string;
};

export type DocumentUploadResult = {
  id: string;
  filename: string;
  status: string;
  stage: string;
};

export type DocumentSummary = DocumentUploadResult & {
  created_at: string;
};

export type ChatAnswer = {
  answer: string;
  citations: string[];
};

export type ChatHistoryMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: string[];
  created_at: string;
};

export type AnalysisSnapshot = {
  id: string;
  status: string;
  summary: string;
  red_flags: string;
  obligations: string;
  follow_up_questions: string;
  created_at: string;
};

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }

  return (await response.json()) as T;
}

function normalizeWorkspaceDetail(
  workspaceId: string,
  payload: Partial<WorkspaceDetail>,
): WorkspaceDetail {
  return {
    id: payload.id ?? workspaceId,
    name: payload.name ?? "Demo workspace",
    status: payload.status ?? "processing",
    documents: payload.documents ?? 0,
    risks: payload.risks ?? 0,
    description: payload.description ?? "Demo fallback until the API is connected.",
    members: payload.members ?? 1,
    recent_activity: payload.recent_activity ?? [],
    documents_list: payload.documents_list ?? [],
    latest_analysis: payload.latest_analysis ?? null,
  };
}

export async function getWorkspaces(): Promise<WorkspaceSummary[]> {
  try {
    return await fetchJson<WorkspaceSummary[]>("/api/workspaces");
  } catch {
    return demoWorkspaces;
  }
}

export async function getWorkspace(workspaceId: string): Promise<WorkspaceDetail> {
  try {
    const payload = await fetchJson<Partial<WorkspaceDetail>>(`/api/workspaces/${workspaceId}`);
    return normalizeWorkspaceDetail(workspaceId, payload);
  } catch {
    const fallback = demoWorkspaces.find((workspace) => workspace.id === workspaceId);
    return normalizeWorkspaceDetail(workspaceId, {
      id: workspaceId,
      name: fallback?.name ?? "Demo workspace",
      status: fallback?.status ?? "processing",
      documents: fallback?.documents ?? 0,
      risks: fallback?.risks ?? 0,
      description: "Demo fallback until the API is connected.",
      members: 1,
      recent_activity: [
        "API fallback mode active",
        "Workspace detail not loaded from backend",
      ],
    });
  }
}

export async function getAuditEvents(workspaceId: string): Promise<AuditEvent[]> {
  try {
    return await fetchJson<AuditEvent[]>(`/api/workspaces/${workspaceId}/audit`);
  } catch {
    return [
      {
        id: `${workspaceId}-audit-1`,
        event_type: "demo.mode",
        message: "Audit timeline is using local fallback data.",
        created_at: "2026-05-02T07:45:00Z",
      },
    ];
  }
}

export async function uploadDocument(
  workspaceId: string,
  file: File,
): Promise<DocumentUploadResult> {
  const formData = new FormData();
  formData.append("workspace_id", workspaceId);
  formData.append("file", file);

  const response = await fetch(`${apiBaseUrl}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }

  return (await response.json()) as DocumentUploadResult;
}

export async function askWorkspaceQuestion(
  workspaceId: string,
  question: string,
): Promise<ChatAnswer> {
  const response = await fetch(`${apiBaseUrl}/api/workspaces/${workspaceId}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Question failed");
  }

  return (await response.json()) as ChatAnswer;
}

export async function getWorkspaceDocuments(workspaceId: string): Promise<DocumentSummary[]> {
  try {
    return await fetchJson<DocumentSummary[]>(`/api/workspaces/${workspaceId}/documents`);
  } catch {
    return [];
  }
}

export async function getWorkspaceChatHistory(workspaceId: string): Promise<ChatHistoryMessage[]> {
  try {
    return await fetchJson<ChatHistoryMessage[]>(`/api/workspaces/${workspaceId}/chat/history`);
  } catch {
    return [];
  }
}
