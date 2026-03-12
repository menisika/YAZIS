import { useState } from "react";
import { useFrequency, useTopN } from "@/api/frequency";
import { Input } from "@/components/Input";
import { Select } from "@/components/Select";
import { Button } from "@/components/Button";
import { Card, CardTitle } from "@/components/Card";
import { Skeleton } from "@/components/Skeleton";
import { ErrorMessage } from "@/components/ErrorMessage";
import { formatNumber } from "@/lib/utils";
import { Search } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const ACCENT = "#f59e0b";
const MUTED = "#334155";

export function FrequenciesPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [by, setBy] = useState<"surface" | "lemma" | "pos">("lemma");
  const [topN, setTopN] = useState(20);
  const [topBy, setTopBy] = useState<"surface" | "lemma" | "pos">("lemma");

  const freqQuery = useFrequency({ q: submittedQuery, by });
  const topQuery = useTopN({ n: topN, by: topBy });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedQuery(query.trim());
  };

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Search section */}
      <section>
        <h2 className="text-sm font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">Word Frequency Lookup</h2>
        <form onSubmit={handleSearch} className="flex gap-3 items-end flex-wrap">
          <Input
            label="Word / Lemma / POS"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. love"
            className="w-48"
          />
          <Select
            label="Field"
            value={by}
            onChange={(e) => setBy(e.target.value as typeof by)}
            options={[
              { value: "surface", label: "Surface Form" },
              { value: "lemma", label: "Lemma" },
              { value: "pos", label: "POS Tag" },
            ]}
          />
          <Button type="submit" className="self-end">
            <Search size={14} /> Look Up
          </Button>
        </form>

        {freqQuery.error && <ErrorMessage message={(freqQuery.error as Error).message} />}

        {freqQuery.data && (
          <div className="mt-5 space-y-4">
            <div className="flex items-center gap-4">
              <div className="text-2xl font-bold">{formatNumber(freqQuery.data.total)}</div>
              <div className="text-sm text-[var(--color-text-muted)]">
                total occurrences of <span className="text-[var(--color-accent)] font-mono">{freqQuery.data.query}</span> ({freqQuery.data.by})
              </div>
            </div>

            {/* Per-text breakdown */}
            <Card>
              <CardTitle>Per-Text Breakdown</CardTitle>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)] text-left">
                      <th className="pb-2 pr-4 font-medium">Text</th>
                      <th className="pb-2 pr-4 font-medium text-right">Count</th>
                      <th className="pb-2 pr-4 font-medium text-right">Rel. Freq (per 1k)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {freqQuery.data.per_text.map((row) => (
                      <tr key={row.text_id} className="border-b border-[var(--color-border)]/50">
                        <td className="py-2 pr-4">
                          <div className="font-medium">{row.title}</div>
                          <div className="text-xs text-[var(--color-text-muted)]">{row.author ?? ""}</div>
                        </td>
                        <td className="py-2 pr-4 text-right font-mono">{formatNumber(row.count)}</td>
                        <td className="py-2 pr-4 text-right font-mono text-[var(--color-accent)]">{row.relative_freq.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}
      </section>

      {/* Top-N section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-[var(--color-text-muted)] uppercase tracking-wide">Top Frequent Terms</h2>
          <div className="flex gap-2 items-center">
            <Select
              value={topBy}
              onChange={(e) => setTopBy(e.target.value as typeof topBy)}
              options={[
                { value: "lemma", label: "Lemma" },
                { value: "surface", label: "Surface" },
                { value: "pos", label: "POS" },
              ]}
            />
            <Select
              value={String(topN)}
              onChange={(e) => setTopN(Number(e.target.value))}
              options={[
                { value: "10", label: "Top 10" },
                { value: "20", label: "Top 20" },
                { value: "50", label: "Top 50" },
              ]}
            />
          </div>
        </div>

        {topQuery.isLoading ? (
          <Skeleton className="h-72 w-full" />
        ) : topQuery.data ? (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
            {/* Bar chart */}
            <Card>
              <CardTitle>Frequency Distribution</CardTitle>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topQuery.data.results} layout="vertical" margin={{ left: 60, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <YAxis type="category" dataKey="term" tick={{ fill: "#94a3b8", fontSize: 11 }} width={80} />
                  <Tooltip
                    contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                    labelStyle={{ color: "#f1f5f9" }}
                    itemStyle={{ color: "#f59e0b" }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {topQuery.data.results.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? ACCENT : MUTED} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* Word cloud style grid */}
            <Card>
              <CardTitle>Word Cloud</CardTitle>
              <div className="flex flex-wrap gap-2 items-center justify-center py-4">
                {topQuery.data.results.map((item, i) => {
                  const max = topQuery.data!.results[0].count;
                  const ratio = item.count / max;
                  const size = 12 + ratio * 24;
                  const opacity = 0.4 + ratio * 0.6;
                  return (
                    <span
                      key={item.term}
                      style={{ fontSize: `${size}px`, opacity, color: i < 3 ? ACCENT : "#94a3b8" }}
                      className="font-medium select-none cursor-default"
                      title={`${item.count} occurrences`}
                    >
                      {item.term}
                    </span>
                  );
                })}
              </div>
            </Card>
          </div>
        ) : null}
      </section>
    </div>
  );
}
