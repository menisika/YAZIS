import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Trash2, FileText, AlertCircle, CheckCircle, X } from "lucide-react";
import { useDocuments, useDeleteDocument, useUploadDocument } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { formatDate, complexityColor, complexityLabel } from "@/lib/utils";
import type { ProcessingSummary } from "@/types";

const ACCEPTED = ".pdf,.docx,.rtf,.txt";

export function LibraryPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useDocuments();
  const deleteMutation = useDeleteDocument();
  const uploadMutation = useUploadDocument();

  const [dragging, setDragging] = useState(false);
  const [lastSummary, setLastSummary] = useState<ProcessingSummary | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    const file = files[0];
    uploadMutation.mutate(file, {
      onSuccess: (summary) => setLastSummary(summary),
    });
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  }

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
      <PageHeader
        title="Document Library"
        subtitle={data ? `${data.total} document${data.total !== 1 ? "s" : ""}` : ""}
        actions={
          <button className="btn btn-primary" onClick={() => fileRef.current?.click()}>
            <Upload size={14} /> Upload
          </button>
        }
      />

      <input
        ref={fileRef}
        type="file"
        accept={ACCEPTED}
        style={{ display: "none" }}
        onChange={(e) => handleFiles(e.target.files)}
      />

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragging ? "var(--accent)" : "var(--border)"}`,
          borderRadius: 12,
          padding: "28px 24px",
          textAlign: "center",
          background: dragging ? "rgba(92,107,192,0.04)" : "transparent",
          cursor: "pointer",
          marginBottom: 28,
          transition: "all 0.2s",
          color: "var(--text-muted)",
          fontSize: 13,
        }}
        onClick={() => fileRef.current?.click()}
      >
        {uploadMutation.isPending ? (
          <span>Processing…</span>
        ) : (
          <>
            <Upload size={20} style={{ margin: "0 auto 8px", display: "block", opacity: 0.5 }} />
            Drop a file here or click to upload
            <br />
            <span style={{ fontSize: 11, opacity: 0.6 }}>PDF, DOCX, RTF, TXT up to 50MB</span>
          </>
        )}
      </div>

      {/* Upload result banner */}
      <AnimatePresence>
        {lastSummary && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              background: "#ecfdf5",
              border: "1px solid #6ee7b7",
              borderRadius: 8,
              padding: "10px 14px",
              marginBottom: 20,
              fontSize: 13,
            }}
          >
            <CheckCircle size={16} color="#059669" />
            <span>
              <strong>{lastSummary.filename}</strong> processed — {lastSummary.sentence_count} sentences,{" "}
              {lastSummary.token_count} tokens in {lastSummary.parse_duration_ms.toFixed(0)}ms
            </span>
            <button
              style={{ marginLeft: "auto", background: "none", border: "none", cursor: "pointer", display: "flex" }}
              onClick={() => setLastSummary(null)}
            >
              <X size={14} />
            </button>
          </motion.div>
        )}

        {uploadMutation.isError && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              background: "#fef2f2",
              border: "1px solid #fca5a5",
              borderRadius: 8,
              padding: "10px 14px",
              marginBottom: 20,
              fontSize: 13,
              color: "#dc2626",
            }}
          >
            <AlertCircle size={16} />
            {uploadMutation.error.message}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document grid */}
      {isLoading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : data?.items.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-muted)" }}>
          <FileText size={40} style={{ margin: "0 auto 12px", opacity: 0.3, display: "block" }} />
          <p>No documents yet. Upload one to get started.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
          {data?.items.map((doc) => (
            <motion.div
              key={doc.id}
              whileHover={{ y: -2, boxShadow: "0 6px 16px rgba(0,0,0,0.1)" }}
              transition={{ duration: 0.15 }}
              className="card"
              style={{ padding: 18, cursor: "pointer", position: "relative" }}
              onClick={() => navigate(`/documents/${doc.id}`)}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 12 }}>
                <FileText size={18} color="var(--accent)" style={{ flexShrink: 0, marginTop: 2 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p
                    style={{
                      fontWeight: 600,
                      fontSize: 14,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {doc.filename}
                  </p>
                  <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    {doc.original_format.toUpperCase()} · {formatDate(doc.uploaded_at)}
                  </p>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 10 }}>
                <Stat label="Sentences" value={doc.sentence_count} />
                <Stat label="Tokens" value={doc.total_tokens} />
                <Stat label="Words" value={doc.word_count} />
                <div>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 2 }}>Avg complexity</p>
                  <span
                    className="badge"
                    style={{
                      background: complexityColor(doc.avg_complexity) + "22",
                      color: complexityColor(doc.avg_complexity),
                    }}
                  >
                    {doc.avg_complexity.toFixed(1)} · {complexityLabel(doc.avg_complexity)}
                  </span>
                </div>
              </div>

              {/* Delete button */}
              <button
                className="btn btn-danger"
                style={{ fontSize: 11, padding: "4px 10px" }}
                onClick={(e) => { e.stopPropagation(); setConfirmDelete(doc.id); }}
              >
                <Trash2 size={12} /> Delete
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {/* Delete confirm dialog */}
      <AnimatePresence>
        {confirmDelete !== null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 50,
            }}
            onClick={() => setConfirmDelete(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="card"
              style={{ padding: 24, width: 320 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 style={{ marginBottom: 10, fontSize: 18 }}>Delete document?</h3>
              <p style={{ color: "var(--text-muted)", marginBottom: 20, fontSize: 13 }}>
                This will permanently delete the document and all its sentences and tokens.
              </p>
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                <button className="btn btn-ghost" onClick={() => setConfirmDelete(null)}>Cancel</button>
                <button
                  className="btn btn-danger"
                  style={{ borderColor: "#dc2626", background: "#dc2626", color: "white" }}
                  onClick={() => {
                    if (confirmDelete !== null) {
                      deleteMutation.mutate(confirmDelete);
                      setConfirmDelete(null);
                    }
                  }}
                >
                  Delete
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 2 }}>{label}</p>
      <p style={{ fontSize: 15, fontWeight: 600 }}>{value.toLocaleString()}</p>
    </div>
  );
}
