"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { VIEWER_COOKIE_NAME } from "../../lib/viewer-session-shared";


export async function signOutViewer() {
  const cookieStore = await cookies();
  cookieStore.delete(VIEWER_COOKIE_NAME);
  redirect("/");
}
