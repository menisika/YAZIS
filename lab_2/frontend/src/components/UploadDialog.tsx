import { useState, useRef, useCallback } from "react";
import { Dialog } from "./Dialog";
import { Button } from "./Button";
import { Input } from "./Input";
import { Upload, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQueryClient } from "@tanstack/react-query";

interface ProgressEvent {
  stage: string;
  progress: number;
  message: string;
}

interface DoneEvent {
  text_id: number;
  progress: number;
  message: string;
}

export function UploadDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [meta, setMeta] = useState({ title: "", author: "", year: "", genre: "", source_url: "" });
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setFile(null);
    setMeta({ title: "", author: "", year: "", genre: "", source_url: "" });
    setProgress(null);
    setDone(false);
    setError(null);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) {
      setFile(f);
      if (!meta.title) setMeta((m) => ({ ...m, title: f.name.replace(/\.[^.]+$/, "") }));
    }
  }, [meta.title]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !meta.title) return;
    setError(null);
    setProgress(null);
    setDone(false);

    const form = new FormData();
    form.append("file", file);
    form.append("title", meta.title);
    if (meta.author) form.append("author", meta.author);
    if (meta.year) form.append("year", meta.year);
    if (meta.genre) form.append("genre", meta.genre);
    if (meta.source_url) form.append("source_url", meta.source_url);

    try {
      const res = await fetch("/api/v1/texts/upload", { method: "POST", body: form });
      if (!res.ok || !res.body) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Upload failed");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";
        for (const chunk of lines) {
          const eventLine = chunk.split("\n").find((l) => l.startsWith("event:"));
          const dataLine = chunk.split("\n").find((l) => l.startsWith("data:"));
          if (!dataLine) continue;
          const data = JSON.parse(dataLine.slice(5));
          const eventType = eventLine?.slice(7).trim();
          if (eventType === "done") {
            setDone(true);
            setProgress({ stage: "done", progress: 100, message: data.message });
            qc.invalidateQueries({ queryKey: ["texts"] });
          } else {
            setProgress(data as ProgressEvent);
          }
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && handleClose()} title="Upload Text" className="max-w-xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Drop zone */}
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
            dragging ? "border-[var(--color-accent)] bg-[var(--color-accent-dim)]" : "border-[var(--color-border)] hover:border-[var(--color-accent)]",
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".txt,.pdf,.docx,.rtf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) {
                setFile(f);
                if (!meta.title) setMeta((m) => ({ ...m, title: f.name.replace(/\.[^.]+$/, "") }));
              }
            }}
          />
          {file ? (
            <div className="flex items-center justify-center gap-2 text-sm">
              <FileText size={18} className="text-[var(--color-accent)]" />
              <span>{file.name}</span>
              <span className="text-[var(--color-text-muted)]">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          ) : (
            <div className="text-[var(--color-text-muted)]">
              <Upload size={24} className="mx-auto mb-2" />
              <p className="text-sm">Drop a file here or click to browse</p>
              <p className="text-xs mt-1">TXT, PDF, DOCX, RTF</p>
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2">
            <Input label="Title *" value={meta.title} onChange={(e) => setMeta((m) => ({ ...m, title: e.target.value }))} required />
          </div>
          <Input label="Author" value={meta.author} onChange={(e) => setMeta((m) => ({ ...m, author: e.target.value }))} />
          <Input label="Year" type="number" value={meta.year} onChange={(e) => setMeta((m) => ({ ...m, year: e.target.value }))} />
          <Input label="Genre" value={meta.genre} onChange={(e) => setMeta((m) => ({ ...m, genre: e.target.value }))} />
          <Input label="Source URL" value={meta.source_url} onChange={(e) => setMeta((m) => ({ ...m, source_url: e.target.value }))} />
        </div>

        {/* Progress */}
        {progress && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[var(--color-text-muted)]">
              <span>{progress.message}</span>
              <span>{progress.progress}%</span>
            </div>
            <div className="h-2 bg-[var(--color-surface-raised)] rounded-full overflow-hidden">
              <div
                className="h-full bg-[var(--color-accent)] transition-all duration-300 rounded-full"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
          </div>
        )}

        {error && <p className="text-sm text-red-400">{error}</p>}
        {done && <p className="text-sm text-green-400">Text ingested successfully!</p>}

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" type="button" onClick={handleClose}>Cancel</Button>
          {!done && (
            <Button type="submit" disabled={!file || !meta.title || !!progress}>
              <Upload size={14} /> Upload
            </Button>
          )}
          {done && (
            <Button type="button" onClick={handleClose}>Done</Button>
          )}
        </div>
      </form>
    </Dialog>
  );
}
