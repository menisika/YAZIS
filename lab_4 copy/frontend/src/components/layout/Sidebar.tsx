import { NavLink, useParams } from "react-router-dom";
import { BookOpen, FileText, PanelLeftClose, Search, Thermometer } from "lucide-react";
import { DEP_GLOSSARY, POS_GLOSSARY, TAG_GLOSSARY, formatGlossaryTooltip } from "@/lib/linguisticGlossary";

export function Sidebar({ onClose }: { onClose: () => void }) {
  const { id } = useParams();

  return (
    <aside
      style={{
        width: 220,
        minHeight: "100vh",
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        padding: "24px 0 16px",
        flexShrink: 0,
        boxShadow: "1px 0 0 var(--border)",
      }}
    >
      <div style={{ padding: "0 20px 16px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <div>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: 22,
              color: "var(--accent)",
              lineHeight: 1,
            }}
          >
            SyntaxLens
          </h1>
          <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 3 }}>
            Syntactic analysis
          </p>
        </div>
        <button
          aria-label="Close sidebar"
          className="btn btn-ghost"
          onClick={onClose}
          style={{ padding: 6, minWidth: "auto", marginTop: -2 }}
        >
          <PanelLeftClose size={14} />
        </button>
      </div>

      <nav style={{ flex: 1, overflowY: "auto" }}>
        <NavSection label="Corpus">
          <SidebarLink to="/" icon={BookOpen} label="Document Library" end />
          <SidebarLink to="/patterns" icon={Search} label="Pattern Search" end />
        </NavSection>

        {id && (
          <NavSection label="Document">
            <SidebarLink
              to={`/documents/${id}`}
              icon={FileText}
              label="Sentence Explorer"
              end
            />
            <SidebarLink
              to={`/documents/${id}/heatmap`}
              icon={Thermometer}
              label="Complexity Heatmap"
              end
            />
          </NavSection>
        )}

        <NavSection label="Glossary">
          <GlossaryGroup title="POS" items={POS_GLOSSARY.slice(0, 10)} />
          <GlossaryGroup title="DEP" items={DEP_GLOSSARY.slice(0, 10)} />
          <GlossaryGroup title="TAG" items={TAG_GLOSSARY.slice(0, 8)} />
        </NavSection>
      </nav>

      <div style={{ padding: "12px 20px" }}>
        <p style={{ fontSize: 10, color: "var(--text-muted)" }}>
          spaCy · en_core_web_lg
        </p>
      </div>
    </aside>
  );
}

function GlossaryGroup({
  title,
  items,
}: {
  title: string;
  items: { code: string; label: string; ruLabel: string; description: string }[];
}) {
  return (
    <div style={{ padding: "2px 20px 8px" }}>
      <p style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 4 }}>{title}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {items.map((item) => (
          <div key={`${title}-${item.code}`} title={formatGlossaryTooltip(item)}>
            <p style={{ fontSize: 11, lineHeight: 1.35 }}>
              <span style={{ color: "var(--text)", fontWeight: 600 }}>{item.label}</span>
              <span style={{ color: "var(--text-muted)", marginLeft: 4, fontFamily: "monospace" }}>{item.code}</span>
            </p>
            <p style={{ fontSize: 10, color: "var(--text-muted)", lineHeight: 1.2 }}>{item.ruLabel}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function NavSection({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <p
        style={{
          fontSize: 10,
          fontWeight: 600,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          padding: "6px 20px 4px",
        }}
      >
        {label}
      </p>
      {children}
    </div>
  );
}

function SidebarLink({
  to,
  icon: Icon,
  label,
  end,
}: {
  to: string;
  icon: React.ElementType;
  label: string;
  end?: boolean;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      style={({ isActive }) => ({
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "7px 20px",
        fontSize: 13,
        fontWeight: isActive ? 600 : 400,
        color: isActive ? "var(--accent)" : "var(--text)",
        background: isActive ? "rgba(92,107,192,0.08)" : "transparent",
        borderLeft: isActive ? "2px solid var(--accent)" : "2px solid transparent",
        transition: "all 0.12s",
        textDecoration: "none",
      })}
    >
      <Icon size={14} />
      {label}
    </NavLink>
  );
}

