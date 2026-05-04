import { redirect } from "next/navigation";

import { AuthPanel } from "../../components/auth-panel";
import { Topbar } from "../../components/topbar";
import { getViewerSession } from "../../lib/viewer-session";

export default async function AuthPage() {
  const viewer = await getViewerSession();
  if (viewer) {
    redirect("/workspaces");
  }

  return (
    <main className="page-shell">
      <Topbar />
      <AuthPanel />
    </main>
  );
}
