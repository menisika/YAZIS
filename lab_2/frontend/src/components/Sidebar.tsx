import { NavLink } from "react-router-dom";
import {
  BookOpen,
  Search,
  AlignLeft,
  BarChart2,
  Sparkles,
  Beaker,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui";

const NAV = [
  { to: "/corpus", icon: BookOpen, label: "Corpus" },
  { to: "/concordance", icon: AlignLeft, label: "Concordance" },
  { to: "/frequencies", icon: BarChart2, label: "Frequencies" },
  { to: "/morphology", icon: Search, label: "Morphology" },
  { to: "/semantic", icon: Sparkles, label: "Semantic Search" },
  { to: "/style-lab", icon: Beaker, label: "Style Lab" },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-[var(--color-surface)] border-r border-[var(--color-border)]",
        "transition-all duration-200",
        sidebarCollapsed ? "w-14" : "w-56",
      )}
    >
      {/* Logo */}
      <div className={cn("flex items-center gap-3 px-4 py-5 border-b border-[var(--color-border)]", sidebarCollapsed && "justify-center px-2")}>
        <div className="w-8 h-8 rounded-lg bg-[var(--color-accent)] flex items-center justify-center shrink-0">
          <BookOpen size={16} className="text-slate-900" />
        </div>
        {!sidebarCollapsed && (
          <span className="font-bold text-sm tracking-wide">Corpus Manager</span>
        )}
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-3 space-y-0.5 px-2">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-2 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-[var(--color-accent-dim)] text-[var(--color-accent)] font-medium"
                  : "text-[var(--color-text-muted)] hover:bg-[var(--color-surface-raised)] hover:text-[var(--color-text)]",
                sidebarCollapsed && "justify-center",
              )
            }
            title={sidebarCollapsed ? label : undefined}
          >
            <Icon size={18} className="shrink-0" />
            {!sidebarCollapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center py-3 border-t border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors cursor-pointer"
      >
        {sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  );
}
