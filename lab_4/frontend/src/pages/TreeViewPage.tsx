import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, Download } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useAnalyzeSemantics, useSentence } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { DependencyTree } from "@/components/ui/DependencyTree";
import { SemanticTree } from "@/components/ui/SemanticTree";
import { ConceptNetPanel } from "@/components/ui/ConceptNetPanel";
import { SemanticAnalysisPanel } from "@/components/ui/SemanticAnalysisPanel";
import { complexityColor, complexityLabel, posColor } from "@/lib/utils";
import { formatGlossaryTooltip, getDepEntry, getPosEntry, getTagEntry } from "@/lib/linguisticGlossary";
import type { TokenResponse } from "@/types";

type ActiveTab = "syntactic" | "semantic";

// ─── Semantic role color (mirrors SemanticTree palette) ──────────────────────

const ROLE_COLORS: Record<string, string> = {
  AGNT: "#ef4444", PAT: "#3b82f6", ACT: "#22c55e", INST: "#f59e0b",
  LOC: "#8b5cf6", ATTR: "#ec4899", RCPT: "#06b6d4", MOD: "#6b7280",
  NEG: "#dc2626", AUX: "#9ca3af", POSS: "#92400e", QUANT: "#65a30d",
  DET: "#d1d5db", CONJ: "#a78bfa", APPOS: "#fb923c",
};
function roleColor(role: string): string {
  return ROLE_COLORS[role] ?? "#9ca3af";
}

export function TreeViewPage() {
  const { id, sentenceId } = useParams<{ id: string; sentenceId: string }>();
  const docId = Number(id);
  const sId = Number(sentenceId);

  const { data: sentence, isLoading } = useSentence(sId);
  const queryClient = useQueryClient();
  const analyzeSemantics = useAnalyzeSemantics();

  const [activeTab, setActiveTab] = useState<ActiveTab>("syntactic");
  const [selectedWord, setSelectedWord] = useState<string | null>(null);

  // Track which sentences have had enrichment triggered this session
  const enrichedSentences = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (activeTab !== "semantic" || sId <= 0) return;
    if (enrichedSentences.current.has(sId)) return;
    enrichedSentences.current.add(sId);
    analyzeSemantics.mutate(sId, {
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sentence", sId] }),
    });
  }, [activeTab, sId]); // eslint-disable-line react-hooks/exhaustive-deps

  const anomalousTokens: TokenResponse[] = sentence?.tokens.filter((t) => t.is_anomalous) ?? [];

  function exportCSV() {
    const url = `http://localhost:8000/api/sentences/${sId}/tokens/csv`;
    const a = document.createElement("a");
    a.href = url;
    a.download = `sentence_${sId}_tokens.csv`;
    a.click();
  }

  function handleNodeClick(token: TokenResponse) {
    setSelectedWord(token.lemma || token.text);
  }

  return (
    <div style={{ padding: 32, maxWidth: 1300, margin: "0 auto" }}>
      {/* Breadcrumbs */}
      <div style={{ marginBottom: 8, display: "flex", gap: 12, alignItems: "center" }}>
        <Link
          to={`/documents/${docId}`}
          style={{ fontSize: 12, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 4 }}
        >
          <ArrowLeft size={12} /> Sentences
        </Link>
        <Link
          to={`/documents/${docId}/heatmap`}
          style={{ fontSize: 12, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 4 }}
        >
          Heatmap <ArrowRight size={12} />
        </Link>
      </div>

      <PageHeader
        title={`Sentence ${sentence ? sentence.index + 1 : "…"}`}
        subtitle={sentence?.text.slice(0, 80) + (sentence && sentence.text.length > 80 ? "…" : "")}
        actions={
          <>
            {sentence && (
              <span
                className="badge"
                style={{
                  background: complexityColor(sentence.complexity_score) + "22",
                  color: complexityColor(sentence.complexity_score),
                  fontSize: 13,
                  padding: "4px 12px",
                }}
              >
                {complexityLabel(sentence.complexity_score)} ({sentence.complexity_score.toFixed(1)})
              </span>
            )}
            <button className="btn btn-ghost" onClick={exportCSV}>
              <Download size={14} /> Export CSV
            </button>
          </>
        }
      />

      {/* ── Tab Switcher ── */}
      <div style={{ display: "flex", gap: 0, marginBottom: 16, borderBottom: "2px solid var(--border)" }}>
        {(["syntactic", "semantic"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              if (tab === "syntactic") setSelectedWord(null);
            }}
            style={{
              background: "none",
              border: "none",
              borderBottom: activeTab === tab ? "2px solid var(--accent)" : "2px solid transparent",
              marginBottom: -2,
              padding: "8px 20px",
              fontSize: 13,
              fontWeight: activeTab === tab ? 700 : 400,
              color: activeTab === tab ? "var(--accent)" : "var(--text-muted)",
              cursor: "pointer",
              textTransform: "capitalize",
              letterSpacing: "0.02em",
              transition: "color 0.15s",
            }}
          >
            {tab === "syntactic" ? "Syntactic Tree" : "Semantic Tree"}
          </button>
        ))}
      </div>

      {/* ── Tree Visualization ── */}
      {isLoading ? (
        <Skeleton height={300} style={{ marginBottom: 24 }} />
      ) : !sentence?.tokens.length ? (
        <p style={{ color: "var(--text-muted)", padding: 24 }}>No tokens available.</p>
      ) : activeTab === "syntactic" ? (
        <div style={{ marginBottom: 24 }}>
          <DependencyTree tokens={sentence.tokens} />
        </div>
      ) : (
        /* ── Semantic Tab ── */
        <>
          {analyzeSemantics.isPending && (
            <div style={{
              marginBottom: 12,
              padding: "8px 14px",
              background: "#eff6ff",
              border: "1px solid #bfdbfe",
              borderRadius: 6,
              fontSize: 12,
              color: "#1d4ed8",
            }}>
              Analyzing semantics…
            </div>
          )}
          <div style={{ display: "flex", gap: 16, marginBottom: 0, alignItems: "flex-start" }}>
            {/* Semantic tree */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <SemanticTree tokens={sentence.tokens} onNodeClick={handleNodeClick} />
            </div>

            {/* ConceptNet side panel */}
            {selectedWord && (
              <ConceptNetPanel word={selectedWord} onClose={() => setSelectedWord(null)} />
            )}
          </div>

          <SemanticAnalysisPanel
            sentenceId={sId}
            originalText={sentence.text}
            anomalousTokens={anomalousTokens}
          />
        </>
      )}

      {/* ── Token Table ── */}
      {sentence && sentence.tokens.length > 0 && (
        <div className="card" style={{ overflow: "auto", marginTop: 24 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "#fafaf8" }}>
                {[
                  "#", "Form", "Lemma", "Part of Speech", "Morphological Tag",
                  "Dependency Relation", "Head",
                  ...(activeTab === "semantic" ? ["Semantic Role"] : []),
                  "Entity",
                ].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: "8px 10px",
                      textAlign: "left",
                      fontWeight: 600,
                      color: "var(--text-muted)",
                      fontSize: 11,
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sentence.tokens.map((tok) => {
                const headToken = sentence.tokens.find((t) => t.index === tok.head_index);
                const posEntry = getPosEntry(tok.pos);
                const tagEntry = getTagEntry(tok.tag);
                const depEntry = getDepEntry(tok.dep);
                return (
                  <tr
                    key={tok.id}
                    style={{
                      borderBottom: "1px solid var(--border)",
                      opacity: tok.is_punct || tok.is_stop ? 0.6 : 1,
                      background: tok.is_anomalous ? "#fef2f222" : undefined,
                    }}
                  >
                    <td style={{ padding: "6px 10px", color: "var(--text-muted)" }}>{tok.index}</td>
                    <td style={{ padding: "6px 10px", fontWeight: 500 }}>
                      {tok.is_anomalous && (
                        <span title={tok.anomaly_reason} style={{ marginRight: 4 }}>⚠</span>
                      )}
                      {tok.text}
                    </td>
                    <td style={{ padding: "6px 10px", color: "var(--text-muted)" }}>{tok.lemma}</td>
                    <td style={{ padding: "6px 10px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "1px 6px",
                          borderRadius: 4,
                          background: posColor(tok.pos) + "22",
                          color: posColor(tok.pos),
                          fontWeight: 500,
                        }}
                        title={formatGlossaryTooltip(posEntry)}
                      >
                        {posEntry.label}
                      </span>
                    </td>
                    <td style={{ padding: "6px 10px" }} title={formatGlossaryTooltip(tagEntry)}>
                      <span style={{ fontSize: 12 }}>{tagEntry.label}</span>
                    </td>
                    <td style={{ padding: "6px 10px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "1px 6px",
                          borderRadius: 4,
                          background: "#5c6bc022",
                          color: "var(--accent)",
                          fontWeight: 500,
                        }}
                        title={formatGlossaryTooltip(depEntry)}
                      >
                        {depEntry.label}
                      </span>
                    </td>
                    <td style={{ padding: "6px 10px", color: "var(--text-muted)" }}>
                      {headToken ? headToken.text : "—"}
                    </td>
                    {activeTab === "semantic" && (
                      <td style={{ padding: "6px 10px" }}>
                        {tok.semantic_label ? (
                          <span
                            style={{
                              display: "inline-block",
                              padding: "1px 6px",
                              borderRadius: 4,
                              background: roleColor(tok.semantic_role) + "22",
                              color: roleColor(tok.semantic_role),
                              fontWeight: 500,
                            }}
                          >
                            {tok.semantic_label}
                          </span>
                        ) : (
                          <span style={{ color: "var(--border)" }}>—</span>
                        )}
                      </td>
                    )}
                    <td style={{ padding: "6px 10px" }}>
                      {tok.ent_type ? (
                        <span
                          style={{
                            display: "inline-block",
                            padding: "1px 6px",
                            borderRadius: 4,
                            background: "#f0fdf4",
                            color: "#16a34a",
                            fontWeight: 500,
                          }}
                        >
                          {tok.ent_type}
                        </span>
                      ) : (
                        <span style={{ color: "var(--border)" }}>—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
