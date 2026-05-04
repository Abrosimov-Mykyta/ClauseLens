"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { VIEWER_COOKIE_NAME } from "../lib/viewer-session-shared";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type AuthMode = "login" | "register";

type SessionPayload = {
  access_token: string;
  mode: "member" | "guest";
  display_name: string;
  email: string;
};

function persistViewerSession(payload: SessionPayload) {
  const session = {
    accessToken: payload.access_token,
    mode: payload.mode,
    displayName: payload.display_name,
    email: payload.email,
  };
  document.cookie = `${VIEWER_COOKIE_NAME}=${encodeURIComponent(JSON.stringify(session))}; path=/; max-age=${60 * 60 * 24 * 14}; SameSite=Lax`;
}

export function AuthPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function handleAuth(endpoint: string, body: Record<string, string> | null) {
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      method: "POST",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || "Authentication failed");
    }

    return (await response.json()) as SessionPayload;
  }

  return (
    <section className="auth-layout" style={{ marginTop: 24 }}>
      <div className="panel">
        <div className="eyebrow">Access ClauseLens</div>
        <h1 className="section-title">{mode === "login" ? "Sign in" : "Create account"}</h1>
        <p className="lede">
          Use a lightweight account for your own review work, or enter immediately as a guest to
          explore the product.
        </p>

        <div className="cta-row">
          <button
            type="button"
            className={mode === "login" ? "button button-primary" : "button button-secondary"}
            onClick={() => setMode("login")}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === "register" ? "button button-primary" : "button button-secondary"}
            onClick={() => setMode("register")}
          >
            Register
          </button>
          <button
            type="button"
            className="button button-subtle"
            disabled={isPending}
            onClick={() => {
              setError(null);
              startTransition(async () => {
                try {
                  const payload = await handleAuth("/api/auth/guest", null);
                  persistViewerSession(payload);
                  router.push("/workspaces");
                  router.refresh();
                } catch (authError) {
                  setError(authError instanceof Error ? authError.message : "Guest access failed");
                }
              });
            }}
          >
            View as guest
          </button>
        </div>

        <div className="composer">
          {mode === "register" ? (
            <>
              <input
                className="composer-input"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                placeholder="Full name"
              />
              <p className="field-hint">This name is used in workspace ownership and the audit trail.</p>
            </>
          ) : null}
          <input
            className="composer-input"
            style={{ marginTop: mode === "register" ? 12 : 0 }}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            type="email"
          />
          <input
            className="composer-input"
            style={{ marginTop: 12 }}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            type="password"
          />
          <p className="field-hint">Use at least 8 characters. This auth flow is intentionally lightweight for the portfolio demo.</p>
          <div className="cta-row">
            <button
              type="button"
              className="button button-primary"
              disabled={
                isPending ||
                !email.trim() ||
                password.trim().length < 8 ||
                (mode === "register" && fullName.trim().length < 2)
              }
              onClick={() => {
                setError(null);
                startTransition(async () => {
                  try {
                    const payload = await handleAuth(
                      mode === "login" ? "/api/auth/login" : "/api/auth/register",
                      mode === "login"
                        ? { email: email.trim(), password: password.trim() }
                        : {
                            full_name: fullName.trim(),
                            email: email.trim(),
                            password: password.trim(),
                          },
                    );
                    persistViewerSession(payload);
                    router.push("/workspaces");
                    router.refresh();
                  } catch (authError) {
                    setError(authError instanceof Error ? authError.message : "Authentication failed");
                  }
                });
              }}
            >
              {isPending ? "Processing..." : mode === "login" ? "Sign in" : "Create account"}
            </button>
          </div>
          {error ? <p className="error-text">{error}</p> : null}
        </div>
      </div>

      <div className="auth-stack">
        <aside className="panel">
          <div className="eyebrow">What happens next</div>
          <div className="stack" style={{ marginTop: 18 }}>
            <div className="callout">
              <h3 className="callout-title">Member account</h3>
              <p className="callout-text">
                Create long-lived workspaces, upload your own files, and keep a personal review history.
              </p>
            </div>
            <div className="callout callout-success">
              <h3 className="callout-title">Guest sandbox</h3>
              <p className="callout-text">
                Enter instantly with a private starter workspace. Great for trying uploads, chat, and citations without registration.
              </p>
            </div>
          </div>
          <ul className="helper-list">
            <li>Private workspace list per session</li>
            <li>Document upload, AI analysis, and grounded Q&amp;A</li>
            <li>Evidence view with chunk-level citations</li>
          </ul>
        </aside>

        <aside className="panel">
          <div className="eyebrow">Portfolio demo note</div>
          <p className="auth-note">
            This authentication layer is intentionally lightweight. It supports account registration,
            sign-in, guest exploration, and per-user workspace ownership without adding password-reset
            flows or enterprise identity providers.
          </p>
        </aside>
      </div>
    </section>
  );
}
