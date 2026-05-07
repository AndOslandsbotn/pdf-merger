export type AppView = "merge" | "faq" | "privacy" | "terms";

export function viewFromHash(hash: string): AppView {
  const path = hash.replace(/^#/, "").replace(/^\//, "").split("/")[0] ?? "";
  if (path === "faq") return "faq";
  if (path === "privacy") return "privacy";
  if (path === "terms") return "terms";
  return "merge";
}

export function hashForView(view: AppView): string {
  return view === "merge" ? "#/" : `#/${view}`;
}
