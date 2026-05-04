export const VIEWER_COOKIE_NAME = "clauselens_viewer";

export type ViewerSession = {
  accessToken: string;
  mode: "member" | "guest";
  displayName: string;
  email: string;
};
