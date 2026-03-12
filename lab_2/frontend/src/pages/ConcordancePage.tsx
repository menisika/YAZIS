import { useState } from "react";
import { useConcordance, type ConcordanceLine } from "@/api/search";
import { Input } from "@/components/Input";
import { Select } from "@/components/Select";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { SkeletonTable } from "@/components/Skeleton";
import { Pagination } from "@/components/Pagination";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Search } from "lucide-react";
import { useUIStore } from "@/stores/ui";
import { Link } from "react-router-dom";

export function ConcordancePage() {
  const { concordanceWindow, setConcordanceWindow } = useUIStore();
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [field, setField] = useState<"surface" | "lemma">("surface");
  const [sortBy, setSortBy] = useState("none");
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useConcordance({
    q: submittedQuery,
    field,
    context: concordanceWindow,
    sort_by: sortBy,
    page,
    page_size: 50,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedQuery(query.trim());
    setPage(1);
  };

  return (
    <div className="space-y-5 max-w-7xl">
      <form onSubmit={handleSearch} className="flex gap-3 flex-wrap items-end">
        <Input
          label="Search Word or Phrase"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. love, war…"
          className="w-56"
        />
        <Select
          label="Match Field"
          value={field}
          onChange={(e) => setField(e.target.value as "surface" | "lemma")}
          options={[
            { value: "surface", label: "Surface Form" },
            { value: "lemma", label: "Lemma" },
          ]}
        />
        <Select
          label="Sort By"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          options={[
            { value: "none", label: "Default" },
            { value: "left", label: "Left Context" },
            { value: "right", label: "Right Context" },
            { value: "author", label: "Author" },
            { value: "year", label: "Year" },
          ]}
        />
        <div className="flex flex-col gap-1">
          <label className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">
            Context ±{concordanceWindow}
          </label>
          <input
            type="range"
            min={1}
            max={15}
            value={concordanceWindow}
            onChange={(e) => setConcordanceWindow(Number(e.target.value))}
            className="h-9 w-32 accent-[var(--color-accent)] cursor-pointer"
          />
        </div>
        <Button type="submit" className="self-end">
          <Search size={14} /> Search
        </Button>
      </form>

      {error && <ErrorMessage message={(error as Error).message} />}

      {submittedQuery && (
        <div className="text-sm text-[var(--color-text-muted)]">
          {isLoading ? "Searching…" : `${data?.total ?? 0} concordance lines for "${submittedQuery}"`}
        </div>
      )}

      {isLoading && submittedQuery && <SkeletonTable rows={10} cols={5} />}

      {data && !isLoading && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)] text-left">
                  <th className="pb-3 pr-4 text-right font-medium w-1/3">Left Context</th>
                  <th className="pb-3 pr-4 text-center font-medium w-32">Match</th>
                  <th className="pb-3 pr-4 font-medium w-1/3">Right Context</th>
                  <th className="pb-3 pr-4 font-medium">Source</th>
                  <th className="pb-3 font-medium">POS</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((line, i) => (
                  <KWICRow key={i} line={line} />
                ))}
                {data.results.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-[var(--color-text-muted)]">
                      No results found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <Pagination page={page} total={data.total} pageSize={data.page_size} onPage={setPage} />
        </>
      )}
    </div>
  );
}

function KWICRow({ line }: { line: ConcordanceLine }) {
  return (
    <tr className="border-b border-[var(--color-border)]/50 hover:bg-[var(--color-surface-raised)]/30">
      <td className="py-2 pr-4 text-right text-[var(--color-text-muted)] font-mono text-xs truncate max-w-xs">
        {line.left}
      </td>
      <td className="py-2 pr-4 text-center">
        <span className="font-bold text-[var(--color-accent)] font-mono">{line.match}</span>
      </td>
      <td className="py-2 pr-4 text-[var(--color-text-muted)] font-mono text-xs truncate max-w-xs">
        {line.right}
      </td>
      <td className="py-2 pr-4 text-xs">
        <Link to={`/corpus/${line.text_id}`} className="hover:text-[var(--color-accent)] transition-colors">
          <div className="font-medium text-[var(--color-text)] truncate max-w-40">{line.title}</div>
          <div className="text-[var(--color-text-muted)]">{[line.author, line.year].filter(Boolean).join(", ")}</div>
        </Link>
      </td>
      <td className="py-2">
        <Badge variant="muted">{line.match_pos}</Badge>
      </td>
    </tr>
  );
}
