import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSemanticSearch, type SemanticResult } from "@/api/semantic";
import { Input } from "@/components/Input";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import { Skeleton, SkeletonCard } from "@/components/Skeleton";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Link } from "react-router-dom";
import { Sparkles, Search } from "lucide-react";

export function SemanticSearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [limit, setLimit] = useState(20);

  const { data, isLoading, error } = useSemanticSearch({ q: submittedQuery, limit });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedQuery(query.trim());
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-[var(--color-accent)]">
          <Sparkles size={18} />
          <h2 className="text-sm font-semibold uppercase tracking-wide">Semantic Passage Search</h2>
        </div>
        <p className="text-sm text-[var(--color-text-muted)]">
          Search by meaning and concept, not just exact words. The system finds thematically related passages across all texts.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 items-end">
        <Input
          label="Natural Language Query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. betrayal and redemption, the horror of war…"
          className="flex-1"
        />
        <div className="flex flex-col gap-1">
          <label className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">Results</label>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md px-3 py-2 text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)]"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
        <Button type="submit" loading={isLoading} className="self-end">
          <Search size={14} /> Search
        </Button>
      </form>

      {error && <ErrorMessage message={(error as Error).message} />}

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      )}

      <AnimatePresence mode="wait">
        {data && !isLoading && (
          <motion.div
            key={data.query}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="space-y-3"
          >
            <p className="text-sm text-[var(--color-text-muted)]">
              {data.results.length} results for <span className="text-[var(--color-text)] italic">"{data.query}"</span>
            </p>
            {data.results.map((result, i) => (
              <ResultCard key={result.sentence_id} result={result} rank={i + 1} />
            ))}
            {data.results.length === 0 && (
              <p className="text-[var(--color-text-muted)] text-sm text-center py-10">
                No results found. Try a different query or upload more texts.
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ResultCard({ result, rank }: { result: SemanticResult; rank: number }) {
  const pct = Math.round(result.similarity * 100);
  const variant = pct >= 80 ? "success" : pct >= 60 ? "accent" : "muted";

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: rank * 0.03 }}
    >
      <Card className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--color-text-muted)] font-mono w-5">{rank}</span>
            <Badge variant={variant}>{pct}% match</Badge>
          </div>
          <Link
            to={`/corpus/${result.text_id}`}
            className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-accent)] transition-colors text-right"
          >
            <div className="font-medium">{result.title}</div>
            <div>{[result.author, result.year].filter(Boolean).join(", ")}</div>
          </Link>
        </div>
        <p className="text-sm leading-relaxed italic text-[var(--color-text)]">
          "{result.content}"
        </p>
        {result.genre && (
          <div className="flex gap-2">
            <Badge variant="muted">{result.genre}</Badge>
          </div>
        )}
      </Card>
    </motion.div>
  );
}
