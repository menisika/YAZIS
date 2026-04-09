import { useState } from "react";
import { AlertTriangle, CheckCircle, RefreshCw } from "lucide-react";
import { useParaphrase } from "@/api/hooks";
import type { TokenResponse } from "@/types";

interface SemanticAnalysisPanelProps {
  sentenceId: number;
  originalText: string;
  anomalousTokens: TokenResponse[];
}

export function SemanticAnalysisPanel({ sentenceId, originalText, anomalousTokens }: SemanticAnalysisPanelProps) {
  const [paraphraseEnabled, setParaphraseEnabled] = useState(false);
  const { data: paraphrase, isLoading, isError } = useParaphrase(sentenceId, paraphraseEnabled);

  return (
    <div className="card" style={{ marginTop: 16, padding: "16px 20px" }}>
      <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 14, color: "var(--text)" }}>
        Semantic Analysis
      </h3>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

        {/* ── Paraphrase Section ── */}
        <div style={{ borderRight: "1px solid var(--border)", paddingRight: 16 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <p style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Synonym Paraphrase
            </p>
            <button
              className="btn btn-ghost"
              style={{ fontSize: 11, padding: "3px 10px", display: "flex", alignItems: "center", gap: 4 }}
              onClick={() => setParaphraseEnabled(true)}
              disabled={paraphraseEnabled && isLoading}
            >
              <RefreshCw size={11} />
              {paraphraseEnabled && isLoading ? "Generating…" : "Paraphrase"}
            </button>
          </div>

          {!paraphraseEnabled && (
            <p style={{ fontSize: 12, color: "var(--text-muted)", fontStyle: "italic" }}>
              Click &ldquo;Paraphrase&rdquo; to replace content words with WordNet synonyms.
            </p>
          )}

          {paraphraseEnabled && isError && (
            <p style={{ fontSize: 12, color: "#ef4444" }}>Failed to generate paraphrase.</p>
          )}

          {paraphrase && (
            <div style={{ fontSize: 12 }}>
              <div style={{ marginBottom: 8 }}>
                <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Original
                </span>
                <p style={{ marginTop: 3, color: "var(--text)", lineHeight: 1.5 }}>{paraphrase.original}</p>
              </div>
              <div>
                <span style={{ fontSize: 10, fontWeight: 600, color: "#22c55e", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Paraphrase
                </span>
                <p style={{ marginTop: 3, color: "var(--text)", lineHeight: 1.5 }}>
                  {buildHighlightedParaphrase(paraphrase.paraphrased, paraphrase.changes.map((c) => c.synonym))}
                </p>
              </div>
              {paraphrase.changes.length > 0 && (
                <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {paraphrase.changes.map((c) => (
                    <span
                      key={c.index}
                      style={{
                        fontSize: 10,
                        padding: "1px 6px",
                        borderRadius: 4,
                        background: "#22c55e22",
                        color: "#16a34a",
                      }}
                      title={`"${c.original_text}" → "${c.synonym}"`}
                    >
                      {c.original_text} → {c.synonym}
                    </span>
                  ))}
                </div>
              )}
              {paraphrase.changes.length === 0 && (
                <p style={{ marginTop: 6, fontSize: 11, color: "var(--text-muted)", fontStyle: "italic" }}>
                  No synonyms found for this sentence.
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Anomaly Detection Section ── */}
        <div>
          <p style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 10 }}>
            Semantic Anomalies
          </p>

          {anomalousTokens.length === 0 ? (
            <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#16a34a" }}>
              <CheckCircle size={14} />
              <span style={{ fontSize: 12 }}>No anomalies detected</span>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {anomalousTokens.map((token) => (
                <div
                  key={token.id}
                  style={{
                    background: "#fef2f2",
                    border: "1px solid #fecaca",
                    borderRadius: 6,
                    padding: "8px 10px",
                    fontSize: 12,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
                    <AlertTriangle size={12} color="#ef4444" />
                    <strong style={{ color: "#dc2626" }}>&ldquo;{token.text}&rdquo;</strong>
                  </div>
                  <p style={{ color: "#6b7280", lineHeight: 1.4 }}>{token.anomaly_reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** Naive word-level highlighting — wraps synonyms with a colored span. */
function buildHighlightedParaphrase(text: string, synonyms: string[]): React.ReactNode {
  const synonymSet = new Set(synonyms.map((s) => s.toLowerCase()));
  const words = text.split(" ");
  return (
    <>
      {words.map((word, i) => {
        const clean = word.replace(/[^a-zA-Z]/g, "").toLowerCase();
        const isNew = synonymSet.has(clean);
        return (
          <span key={i}>
            {i > 0 && " "}
            {isNew ? (
              <mark style={{ background: "#bbf7d0", borderRadius: 2, padding: "0 2px" }}>{word}</mark>
            ) : (
              word
            )}
          </span>
        );
      })}
    </>
  );
}
