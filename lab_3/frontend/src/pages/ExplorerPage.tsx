import { useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, GitBranch, Search, SlidersHorizontal, Thermometer } from "lucide-react";
import { useDocument, useSentences } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { complexityColor } from "@/lib/utils";

const PAGE_SIZE = 30;

export function ExplorerPage() {
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);
  const navigate = useNavigate();

  const [offset, setOffset] = useState(0);
  const [keyword, setKeyword] = useState("");
  const [minC, setMinC] = useState<number | undefined>(undefined);
  const [maxC, setMaxC] = useState<number | undefined>(undefined);
  const [showFilters, setShowFilters] = useState(false);

  const { data: doc } = useDocument(docId);
  const { data, isLoading } = useSentences(docId, {
    offset,
    limit: PAGE_SIZE,
    keyword: keyword || undefined,
    min_complexity: minC,
    max_complexity: maxC,
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;
  const currentPage = Math.floor(offset / PAGE_SIZE);

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ marginBottom: 8 }}>
        <Link
          to="/"
          style={{ fontSize: 12, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 4 }}
        >
          <ArrowLeft size={12} /> Library
        </Link>
      </div>

      <PageHeader
        title={doc?.filename ?? "Sentence Explorer"}
        subtitle={data ? `${data.total} sentences` : ""}
        actions={
          <Link to={`/documents/${docId}/heatmap`} className="btn btn-ghost">
            <Thermometer size={14} /> Heatmap
          </Link>
        }
      />

      {/* Filters */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 10, marginBottom: showFilters ? 12 : 0 }}>
          <div style={{ position: "relative", flex: 1 }}>
            <Search size={14} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
            <input
              placeholder="Search sentences…"
              value={keyword}
              onChange={(e) => { setKeyword(e.target.value); setOffset(0); }}
              style={{ paddingLeft: 32 }}
            />
          </div>
          <button
            className={`btn ${showFilters ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setShowFilters((v) => !v)}
          >
            <SlidersHorizontal size={14} /> Filters
          </button>
        </div>

        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            style={{
              display: "flex",
              gap: 12,
              padding: "12px 16px",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
            }}
          >
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 11, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>
                Min complexity
              </label>
              <input
                type="number"
                min={0}
                max={100}
                placeholder="0"
                value={minC ?? ""}
                onChange={(e) => { setMinC(e.target.value ? Number(e.target.value) : undefined); setOffset(0); }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 11, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>
                Max complexity
              </label>
              <input
                type="number"
                min={0}
                max={100}
                placeholder="100"
                value={maxC ?? ""}
                onChange={(e) => { setMaxC(e.target.value ? Number(e.target.value) : undefined); setOffset(0); }}
              />
            </div>
          </motion.div>
        )}
      </div>

      {/* Sentence list */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {isLoading
          ? Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card" style={{ padding: 14 }}>
                <Skeleton height={14} width="90%" style={{ marginBottom: 8 }} />
                <Skeleton height={12} width="30%" />
              </div>
            ))
          : data?.items.map((sent) => (
              <motion.div
                key={sent.id}
                whileHover={{ x: 2 }}
                transition={{ duration: 0.1 }}
                className="card"
                style={{ padding: 14, cursor: "pointer", display: "flex", alignItems: "center", gap: 12 }}
                onClick={() => navigate(`/documents/${docId}/sentences/${sent.id}`)}
              >
                <span style={{ fontSize: 11, color: "var(--text-muted)", minWidth: 28, textAlign: "right" }}>
                  {sent.index + 1}
                </span>
                <p style={{ flex: 1, fontSize: 13, lineHeight: 1.5 }}>{sent.text}</p>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexShrink: 0 }}>
                  <span
                    className="badge"
                    style={{
                      background: complexityColor(sent.complexity_score) + "22",
                      color: complexityColor(sent.complexity_score),
                    }}
                  >
                    {sent.complexity_score.toFixed(0)}
                  </span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{sent.token_count}t</span>
                  <GitBranch size={14} color="var(--accent)" />
                </div>
              </motion.div>
            ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
          <button
            className="btn btn-ghost"
            disabled={currentPage === 0}
            onClick={() => setOffset((p) => Math.max(0, p - PAGE_SIZE))}
          >
            ← Prev
          </button>
          <span style={{ display: "flex", alignItems: "center", fontSize: 13, color: "var(--text-muted)" }}>
            {currentPage + 1} / {totalPages}
          </span>
          <button
            className="btn btn-ghost"
            disabled={currentPage >= totalPages - 1}
            onClick={() => setOffset((p) => p + PAGE_SIZE)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
