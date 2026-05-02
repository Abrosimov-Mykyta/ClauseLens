export type WorkspaceSummary = {
  id: string;
  name: string;
  status: "ready" | "processing";
  documents: number;
  risks: number;
  updatedAt: string;
};

export const workspaces: WorkspaceSummary[] = [
  {
    id: "ws-acme",
    name: "Acme Acquisition Review",
    status: "ready",
    documents: 14,
    risks: 6,
    updatedAt: "Updated 8 minutes ago",
  },
  {
    id: "ws-northstar",
    name: "Northstar Vendor Audit",
    status: "processing",
    documents: 5,
    risks: 2,
    updatedAt: "Parsing 2 fresh uploads",
  },
  {
    id: "ws-orbit",
    name: "Orbit Financing Pack",
    status: "ready",
    documents: 9,
    risks: 4,
    updatedAt: "Q&A session active",
  },
];

export const highlights = [
  "Change-of-control language appears in 3 contracts",
  "Two indemnity clauses exceed the configured risk threshold",
  "Missing termination notice period in one supplier agreement",
];

