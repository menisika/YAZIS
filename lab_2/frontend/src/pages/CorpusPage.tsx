import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTexts, useDeleteText, type TextSummary } from "@/api/corpus";
import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { Badge } from "@/components/Badge";
import { Skeleton, SkeletonTable } from "@/components/Skeleton";
import { Pagination } from "@/components/Pagination";
import { ErrorMessage } from "@/components/ErrorMessage";
import { UploadDialog } from "@/components/UploadDialog";
import { formatNumber } from "@/lib/utils";
import { Upload, Trash2, ExternalLink, ChevronRight } from "lucide-react";

export function CorpusPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [author, setAuthor] = useState("");
  const [genre, setGenre] = useState("");
  const [page, setPage] = useState(1);
  const [uploadOpen, setUploadOpen] = useState(false);
  const deleteMut = useDeleteText();

  const { data, isLoading, error } = useTexts({
    search: search || undefined,
    author: author || undefined,
    genre: genre || undefined,
    page,
    page_size: 20,
  });

  return (
    <div className="space-y-5 max-w-6xl">
      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-3 flex-1">
          <Input placeholder="Search titles…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="w-52" />
          <Input placeholder="Author…" value={author} onChange={(e) => { setAuthor(e.target.value); setPage(1); }} className="w-40" />
          <Input placeholder="Genre…" value={genre} onChange={(e) => { setGenre(e.target.value); setPage(1); }} className="w-36" />
        </div>
        <Button onClick={() => setUploadOpen(true)}>
          <Upload size={14} /> Upload Text
        </Button>
      </div>

      {error && <ErrorMessage message={(error as Error).message} />}

      {isLoading ? (
        <SkeletonTable rows={8} cols={5} />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)] text-left">
                <th className="pb-3 pr-4 font-medium">Title</th>
                <th className="pb-3 pr-4 font-medium">Author</th>
                <th className="pb-3 pr-4 font-medium">Year</th>
                <th className="pb-3 pr-4 font-medium">Genre</th>
                <th className="pb-3 pr-4 font-medium text-right">Tokens</th>
                <th className="pb-3 pr-4 font-medium text-right">Sentences</th>
                <th className="pb-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.results.map((text) => (
                <TextRow
                  key={text.id}
                  text={text}
                  onView={() => navigate(`/corpus/${text.id}`)}
                  onDelete={() => deleteMut.mutate(text.id)}
                />
              ))}
              {data?.results.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-[var(--color-text-muted)]">
                    No texts in corpus yet. Upload one to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {data && (
        <Pagination page={page} total={data.total} pageSize={data.page_size} onPage={setPage} />
      )}

      <UploadDialog open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </div>
  );
}

function TextRow({ text, onView, onDelete }: { text: TextSummary; onView: () => void; onDelete: () => void }) {
  return (
    <tr
      className="border-b border-[var(--color-border)]/50 hover:bg-[var(--color-surface-raised)]/50 cursor-pointer transition-colors"
      onClick={onView}
    >
      <td className="py-3 pr-4">
        <div className="flex items-center gap-2">
          <span className="font-medium text-[var(--color-text)]">{text.title}</span>
          {text.source_url && <ExternalLink size={12} className="text-[var(--color-text-muted)]" />}
        </div>
      </td>
      <td className="py-3 pr-4 text-[var(--color-text-muted)]">{text.author ?? "—"}</td>
      <td className="py-3 pr-4 text-[var(--color-text-muted)]">{text.year ?? "—"}</td>
      <td className="py-3 pr-4">
        {text.genre ? <Badge variant="muted">{text.genre}</Badge> : <span className="text-[var(--color-text-muted)]">—</span>}
      </td>
      <td className="py-3 pr-4 text-right text-[var(--color-text-muted)]">{formatNumber(text.token_count)}</td>
      <td className="py-3 pr-4 text-right text-[var(--color-text-muted)]">{formatNumber(text.sentence_count)}</td>
      <td className="py-3 text-right">
        <div className="flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
          <Button variant="ghost" size="sm" onClick={onView}>
            <ChevronRight size={14} />
          </Button>
          <Button variant="ghost" size="sm" onClick={onDelete} className="text-red-400 hover:text-red-300">
            <Trash2 size={14} />
          </Button>
        </div>
      </td>
    </tr>
  );
}
