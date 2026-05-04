import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { VIEWER_COOKIE_NAME, type ViewerSession } from "./viewer-session-shared";

export async function getViewerSession(): Promise<ViewerSession | null> {
  const cookieStore = await cookies();
  const rawValue = cookieStore.get(VIEWER_COOKIE_NAME)?.value;
  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(decodeURIComponent(rawValue)) as ViewerSession;
  } catch {
    return null;
  }
}

export async function requireViewerSession(): Promise<ViewerSession> {
  const session = await getViewerSession();
  if (!session) {
    redirect("/auth");
  }

  return session;
}
