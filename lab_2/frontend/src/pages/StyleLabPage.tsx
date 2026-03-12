import { useState } from "react";
import { useTexts } from "@/api/corpus";
import { useCompareTexts, type TextStyle } from "@/api/style";
import { Card, CardTitle } from "@/components/Card";
import { Skeleton } from "@/components/Skeleton";
import { ErrorMessage } from "@/components/ErrorMessage";
import { useUIStore } from "@/stores/ui";
import { Badge } from "@/components/Badge";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from "recharts";
import { X } from "lucide-react";

const COLORS = ["#f59e0b", "#38bdf8", "#a78bfa", "#34d399"];

export function StyleLabPage() {
  const { selectedTextIds, toggleSelectedText, setSelectedTextIds } = useUIStore();
  const { data: textsData } = useTexts({ page_size: 100 });
  const { data: comparison, isLoading, error } = useCompareTexts(selectedTextIds);

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Text selection */}
      <section>
        <h2 className="text-sm font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">
          Select 2–4 Texts to Compare
        </h2>
        {selectedTextIds.length > 0 && (
          <div className="flex gap-2 flex-wrap mb-3">
            {selectedTextIds.map((id, i) => {
              const text = textsData?.results.find((t) => t.id === id);
              return (
                <span
                  key={id}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border"
                  style={{ borderColor: COLORS[i], color: COLORS[i] }}
                >
                  {text?.title ?? `Text #${id}`}
                  <button onClick={() => toggleSelectedText(id)} className="cursor-pointer">
                    <X size={12} />
                  </button>
                </span>
              );
            })}
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2 max-h-48 overflow-y-auto pr-1">
          {textsData?.results.map((text) => {
            const idx = selectedTextIds.indexOf(text.id);
            const isSelected = idx !== -1;
            const isFull = selectedTextIds.length >= 4 && !isSelected;
            return (
              <button
                key={text.id}
                onClick={() => !isFull && toggleSelectedText(text.id)}
                disabled={isFull}
                className={`text-left px-3 py-2 rounded-md border text-sm transition-colors cursor-pointer ${
                  isSelected
                    ? "border-[var(--color-accent)] bg-[var(--color-accent-dim)]"
                    : "border-[var(--color-border)] hover:border-[var(--color-text-muted)]"
                } ${isFull ? "opacity-40 cursor-not-allowed" : ""}`}
              >
                <div className="font-medium truncate">{text.title}</div>
                <div className="text-xs text-[var(--color-text-muted)]">{text.author ?? "Unknown"}</div>
              </button>
            );
          })}
        </div>
      </section>

      {error && <ErrorMessage message={(error as Error).message} />}

      {isLoading && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-72" />)}
        </div>
      )}

      {comparison && !isLoading && comparison.texts.length >= 2 && (
        <ComparisonView texts={comparison.texts} />
      )}

      {selectedTextIds.length < 2 && !isLoading && (
        <p className="text-sm text-[var(--color-text-muted)] text-center py-10">
          Select at least 2 texts above to see the style comparison.
        </p>
      )}
    </div>
  );
}

function ComparisonView({ texts }: { texts: TextStyle[] }) {
  // POS radar data
  const radarData = ["NOUN", "VERB", "ADJ", "ADV", "OTHER"].map((pos) => ({
    subject: pos,
    ...Object.fromEntries(texts.map((t, i) => [t.title.slice(0, 15), t.pos_distribution[pos as keyof typeof t.pos_distribution]])),
  }));

  // Metric bar charts
  const metrics: { key: keyof TextStyle["metrics"]; label: string }[] = [
    { key: "ttr", label: "Type-Token Ratio" },
    { key: "mtld", label: "MTLD" },
    { key: "avg_sentence_length", label: "Avg Sentence Length" },
    { key: "lexical_density", label: "Lexical Density" },
    { key: "flesch_kincaid", label: "Flesch-Kincaid" },
  ];

  const metricsData = metrics.map(({ key, label }) => ({
    name: label,
    ...Object.fromEntries(texts.map((t, i) => [t.title.slice(0, 15), t.metrics[key]])),
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        {/* Radar chart */}
        <Card>
          <CardTitle>POS Distribution Profile</CardTitle>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <PolarRadiusAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
              {texts.map((t, i) => (
                <Radar
                  key={t.text_id}
                  name={t.title.slice(0, 20)}
                  dataKey={t.title.slice(0, 15)}
                  stroke={COLORS[i]}
                  fill={COLORS[i]}
                  fillOpacity={0.15}
                />
              ))}
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        {/* Metrics bar chart */}
        <Card>
          <CardTitle>Linguistic Metrics</CardTitle>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={metricsData} layout="vertical" margin={{ left: 120, right: 20 }}>
              <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} width={120} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              {texts.map((t, i) => (
                <Bar key={t.text_id} dataKey={t.title.slice(0, 15)} fill={COLORS[i]} radius={[0, 3, 3, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Distinctive words per text */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {texts.map((text, i) => (
          <Card key={text.text_id}>
            <CardTitle style={{ color: COLORS[i] }}>{text.title.slice(0, 25)}</CardTitle>
            <div className="space-y-1">
              {(text.distinctive_words ?? text.top_content_lemmas.slice(0, 10)).slice(0, 15).map((item, j) => (
                <div key={j} className="flex items-center justify-between text-xs">
                  <span className="font-mono text-[var(--color-text)]">
                    {"lemma" in item ? item.lemma : ""}
                  </span>
                  <span className="text-[var(--color-text-muted)]">
                    {"score" in item ? item.score.toFixed(4) : ("count" in item ? item.count : "")}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>

      {/* Summary stats table */}
      <Card>
        <CardTitle>Summary Statistics</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)] text-left">
                <th className="pb-2 pr-4 font-medium">Text</th>
                <th className="pb-2 pr-4 font-medium text-right">Tokens</th>
                <th className="pb-2 pr-4 font-medium text-right">TTR</th>
                <th className="pb-2 pr-4 font-medium text-right">MTLD</th>
                <th className="pb-2 pr-4 font-medium text-right">Avg Sent Len</th>
                <th className="pb-2 pr-4 font-medium text-right">Lex Density</th>
                <th className="pb-2 font-medium text-right">Flesch-Kincaid</th>
              </tr>
            </thead>
            <tbody>
              {texts.map((t, i) => (
                <tr key={t.text_id} className="border-b border-[var(--color-border)]/50">
                  <td className="py-2 pr-4">
                    <span style={{ color: COLORS[i] }} className="font-medium">●</span>
                    <span className="ml-2">{t.title}</span>
                  </td>
                  <td className="py-2 pr-4 text-right font-mono">{t.token_count.toLocaleString()}</td>
                  <td className="py-2 pr-4 text-right font-mono">{t.metrics.ttr.toFixed(3)}</td>
                  <td className="py-2 pr-4 text-right font-mono">{t.metrics.mtld.toFixed(1)}</td>
                  <td className="py-2 pr-4 text-right font-mono">{t.metrics.avg_sentence_length.toFixed(1)}</td>
                  <td className="py-2 pr-4 text-right font-mono">{(t.metrics.lexical_density * 100).toFixed(1)}%</td>
                  <td className="py-2 text-right font-mono">{t.metrics.flesch_kincaid.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
