import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useText, useAnnotatedContent, type AnnotatedToken } from "@/api/corpus";
import { Card, CardTitle } from "@/components/Card";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { Skeleton } from "@/components/Skeleton";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { formatNumber } from "@/lib/utils";
import { ArrowLeft } from "lucide-react";

const POS_COLORS: Record<string, string> = {
  NOUN: "text-blue-300",
  VERB: "text-green-300",
  ADJ: "text-purple-300",
  ADV: "text-yellow-300",
  PROPN: "text-amber-300",
};

function TokenSpan({ token }: { token: AnnotatedToken }) {
  const [tip, setTip] = useState(false);
  const morphStr = token.morph
    ? Object.entries(token.morph)
        .map(([k, v]) => `${k}=${v.join(",")}`)
        .join(" | ")
    : null;

  return (
    <span className="relative inline-block" onMouseEnter={() => setTip(true)} onMouseLeave={() => setTip(false)}>
      <span className={`cursor-default hover:underline decoration-dotted ${POS_COLORS[token.pos] ?? ""}`}>
        {token.surface}
      </span>
      {tip && (
        <span className="absolute bottom-full left-0 z-10 mb-1 whitespace-nowrap bg-[var(--color-surface-raised)] border border-[var(--color-border)] rounded px-2 py-1 text-xs shadow-lg">
          <span className="font-mono text-[var(--color-accent)]">{token.lemma}</span>
          <span className="text-[var(--color-text-muted)] ml-2">{token.pos}</span>
          {morphStr && <span className="text-[var(--color-text-muted)] ml-2">{morphStr}</span>}
        </span>
      )}
    </span>
  );
}

export function TextDetailPage() {
  const { id } = useParams<{ id: string }>();
  const textId = Number(id);
  const [page, setPage] = useState(1);
  const pageSize = 500;

  const { data: textMeta, isLoading: metaLoading, error: metaError } = useText(textId);
  const { data: content, isLoading: contentLoading } = useAnnotatedContent(textId, page, pageSize);

  if (metaError) return <ErrorMessage message={(metaError as Error).message} />;

  return (
    <div className="max-w-5xl space-y-4">
      <Link to="/corpus" className="inline-flex items-center gap-1 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)]">
        <ArrowLeft size={14} /> Back to Corpus
      </Link>

      {metaLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-7 w-1/2" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      ) : textMeta && (
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h2 className="text-xl font-semibold">{textMeta.title}</h2>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              {[textMeta.author, textMeta.year, textMeta.genre].filter(Boolean).join(" · ")}
            </p>
          </div>
          <div className="flex gap-3">
            <Card className="px-4 py-2 text-center min-w-24">
              <div className="text-lg font-bold text-[var(--color-accent)]">{formatNumber(textMeta.token_count)}</div>
              <div className="text-xs text-[var(--color-text-muted)]">tokens</div>
            </Card>
            <Card className="px-4 py-2 text-center min-w-24">
              <div className="text-lg font-bold text-[var(--color-accent)]">{formatNumber(textMeta.sentence_count)}</div>
              <div className="text-xs text-[var(--color-text-muted)]">sentences</div>
            </Card>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex gap-3 text-xs text-[var(--color-text-muted)] flex-wrap">
        {Object.entries(POS_COLORS).map(([pos, cls]) => (
          <span key={pos} className={cls}>● {pos}</span>
        ))}
        <span>Hover any word for lemma + morphology</span>
      </div>

      {/* Annotated text */}
      <Card className="font-serif leading-8 text-base">
        {contentLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-5 w-full" />)}
          </div>
        ) : content?.tokens ? (
          <div className="flex flex-wrap gap-x-1">
            {content.tokens.map((tok, i) => (
              <TokenSpan key={i} token={tok} />
            ))}
          </div>
        ) : null}
      </Card>

      {content && (
        <Pagination
          page={page}
          total={content.total_tokens}
          pageSize={pageSize}
          onPage={setPage}
        />
      )}
    </div>
  );
}
