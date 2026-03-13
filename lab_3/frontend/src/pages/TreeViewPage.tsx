import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, Download } from "lucide-react";
import { useSentence } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { DependencyTree } from "@/components/ui/DependencyTree";
import { complexityColor, complexityLabel, posColor } from "@/lib/utils";
import { formatGlossaryTooltip, getDepEntry, getPosEntry, getTagEntry } from "@/lib/linguisticGlossary";

export function TreeViewPage() {
  const { id, sentenceId } = useParams<{ id: string; sentenceId: string }>();
  const docId = Number(id);
  const sId = Number(sentenceId);

  const { data: sentence, isLoading } = useSentence(sId);

  function exportCSV() {
    const url = `http://localhost:8000/api/sentences/${sId}/tokens/csv`;
    const a = document.createElement("a");
    a.href = url;
    a.download = `sentence_${sId}_tokens.csv`;
    a.click();
  }

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
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

      {isLoading ? (
        <Skeleton height={300} style={{ marginBottom: 24 }} />
      ) : sentence?.tokens.length ? (
        <div style={{ marginBottom: 24 }}>
          <DependencyTree tokens={sentence.tokens} />
        </div>
      ) : (
        <p style={{ color: "var(--text-muted)", padding: 24 }}>No tokens available.</p>
      )}

      {/* Token table */}
      {sentence && sentence.tokens.length > 0 && (
        <div className="card" style={{ overflow: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "#fafaf8" }}>
                {["#", "Form", "Lemma", "Part of Speech", "Morphological Tag", "Dependency Relation", "Head", "Entity"].map((h) => (
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
                    }}
                  >
                    <td style={{ padding: "6px 10px", color: "var(--text-muted)" }}>{tok.index}</td>
                    <td style={{ padding: "6px 10px", fontWeight: 500 }}>{tok.text}</td>
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
