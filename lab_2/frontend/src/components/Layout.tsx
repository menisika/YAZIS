import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";

const PAGE_TITLES: Record<string, string> = {
  "/corpus": "Corpus",
  "/concordance": "Concordance",
  "/frequencies": "Frequencies",
  "/morphology": "Morphology",
  "/semantic": "Semantic Search",
  "/style-lab": "Style Lab",
};

export function Layout() {
  const loc = useLocation();
  const title = Object.entries(PAGE_TITLES).find(([p]) => loc.pathname.startsWith(p))?.[1] ?? "Corpus Manager";

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center h-14 px-6 border-b border-[var(--color-border)] shrink-0 bg-[var(--color-bg)]">
          <h1 className="text-base font-semibold">{title}</h1>
        </header>
        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
