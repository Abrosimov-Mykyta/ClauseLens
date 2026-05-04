import Link from "next/link";

import { signOutViewer } from "../app/auth/actions";
import { getViewerSession } from "../lib/viewer-session";

export async function Topbar() {
  const viewer = await getViewerSession();

  return (
    <header className="topbar">
      <Link href="/" className="brand">
        ClauseLens
      </Link>
      <nav className="nav-links" aria-label="Primary navigation">
        {viewer ? (
          <>
            <Link href="/workspaces">Workspaces</Link>
            <Link href="/auth">Account</Link>
            <span className="status-pill status-pill-neutral">
              {viewer.mode === "guest" ? "Guest sandbox" : viewer.displayName}
            </span>
            <form action={signOutViewer}>
              <button type="submit" className="button button-secondary">
                Sign out
              </button>
            </form>
          </>
        ) : (
          <Link href="/auth">Login / Guest access</Link>
        )}
      </nav>
    </header>
  );
}
