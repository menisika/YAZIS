import { useState } from "react";
import { useGrammarCard, type MorphForm } from "@/api/morphology";
import { Input } from "@/components/Input";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { Card, CardTitle } from "@/components/Card";
import { Skeleton } from "@/components/Skeleton";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { formatNumber } from "@/lib/utils";
import { formatMorphBadge, formatPosLabel } from "@/lib/linguisticLabels";

export function MorphologyPage() {
  const [query, setQuery] = useState("");
  const [submittedLemma, setSubmittedLemma] = useState("");

  const { data, isLoading, error } = useGrammarCard(submittedLemma);

  return (
    <div className="space-y-6 max-w-4xl">
      <form
        onSubmit={(e) => { e.preventDefault(); setSubmittedLemma(query.trim().toLowerCase()); }}
        className="flex gap-3 items-end"
      >
        <Input
          label="Lemma"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. run, love, good…"
          className="w-56"
        />
        <Button type="submit" className="self-end">
          <Search size={14} /> Look Up
        </Button>
      </form>

      {error && (
        <ErrorMessage message={`Lemma "${submittedLemma}" not found in corpus`} />
      )}

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28 w-full" />)}
        </div>
      )}

      {data && !isLoading && (
        <div className="space-y-5">
          <div className="flex items-baseline gap-3">
            <h2 className="text-2xl font-bold font-mono text-[var(--color-accent)]">{data.lemma}</h2>
            <span className="text-sm text-[var(--color-text-muted)]">
              {formatNumber(data.total_occurrences)} total occurrences · {data.forms.length} attested forms
            </span>
          </div>

          <div className="space-y-3">
            {data.forms.map((form, i) => (
              <FormCard key={i} form={form} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function FormCard({ form }: { form: MorphForm }) {
  const [expanded, setExpanded] = useState(false);
  const morphEntries = Object.entries(form.morph ?? {});

  return (
    <Card className="space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-mono font-bold text-lg">{form.surface}</span>
          <Badge variant="muted">{formatPosLabel(form.pos)}</Badge>
          <Badge variant="accent">{formatNumber(form.count)} occ.</Badge>
          {morphEntries.map(([k, v]) => (
            <Badge key={k} variant="muted">
              {formatMorphBadge(k, v)}
            </Badge>
          ))}
        </div>
        {form.examples.length > 0 && (
          <button
            onClick={() => setExpanded((p) => !p)}
            className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] shrink-0 cursor-pointer"
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        )}
      </div>

      {expanded && form.examples.length > 0 && (
        <div className="space-y-2 border-t border-[var(--color-border)] pt-3">
          <CardTitle className="mb-0">Example Sentences</CardTitle>
          {form.examples.map((ex, i) => (
            <p key={i} className="text-sm text-[var(--color-text-muted)] italic leading-relaxed">
              "{ex}"
            </p>
          ))}
        </div>
      )}
    </Card>
  );
}
