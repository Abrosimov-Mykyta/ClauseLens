import Link from "next/link";

export function Topbar() {
  return (
    <header className="topbar">
      <Link href="/" className="brand">
        ClauseLens
      </Link>
      <nav className="nav-links" aria-label="Primary navigation">
        <Link href="/workspaces">Workspaces</Link>
        <Link href="/workspaces/ws-acme">Review</Link>
        <Link href="/workspaces/ws-acme/chat">AI Chat</Link>
      </nav>
    </header>
  );
}

