import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  ConceptNetResponse,
  DocumentListItem,
  DocumentResponse,
  DocumentsPage,
  ParaphraseResponse,
  PatternQuery,
  PatternSearchResponse,
  ProcessingSummary,
  SentenceListItem,
  SentenceResponse,
  SentencesPage,
  TokenResponse,
  WordNetResponse,
} from "@/types";

// ─── Documents ────────────────────────────────────────────────────────────────

export function useDocuments(offset = 0, limit = 20) {
  return useQuery<DocumentsPage>({
    queryKey: ["documents", offset, limit],
    queryFn: () => api.get(`/documents?offset=${offset}&limit=${limit}`),
  });
}

export function useDocument(id: number) {
  return useQuery<DocumentResponse>({
    queryKey: ["document", id],
    queryFn: () => api.get(`/documents/${id}`),
    enabled: id > 0,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation<ProcessingSummary, Error, File>({
    mutationFn: (file) => api.upload("/documents/upload", file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (id) => api.delete(`/documents/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}

// ─── Sentences ────────────────────────────────────────────────────────────────

interface SentenceFilters {
  offset?: number;
  limit?: number;
  min_complexity?: number;
  max_complexity?: number;
  keyword?: string;
}

export function useSentences(documentId: number, filters: SentenceFilters = {}) {
  const params = new URLSearchParams();
  params.set("offset", String(filters.offset ?? 0));
  params.set("limit", String(filters.limit ?? 50));
  if (filters.min_complexity !== undefined) params.set("min_complexity", String(filters.min_complexity));
  if (filters.max_complexity !== undefined) params.set("max_complexity", String(filters.max_complexity));
  if (filters.keyword) params.set("keyword", filters.keyword);

  return useQuery<SentencesPage>({
    queryKey: ["sentences", documentId, filters],
    queryFn: () => api.get(`/documents/${documentId}/sentences?${params}`),
    enabled: documentId > 0,
  });
}

export function useAllSentences(documentId: number) {
  return useQuery<SentenceListItem[]>({
    queryKey: ["sentences-all", documentId],
    queryFn: () => api.get(`/documents/${documentId}/sentences/all`),
    enabled: documentId > 0,
  });
}

export function useSentence(sentenceId: number) {
  return useQuery<SentenceResponse>({
    queryKey: ["sentence", sentenceId],
    queryFn: () => api.get(`/sentences/${sentenceId}`),
    enabled: sentenceId > 0,
  });
}

// ─── Tokens ───────────────────────────────────────────────────────────────────

export function useTokens(sentenceId: number) {
  return useQuery<TokenResponse[]>({
    queryKey: ["tokens", sentenceId],
    queryFn: () => api.get(`/sentences/${sentenceId}/tokens`),
    enabled: sentenceId > 0,
  });
}

// ─── Patterns ─────────────────────────────────────────────────────────────────

export function usePatternSearch() {
  return useMutation<PatternSearchResponse, Error, PatternQuery>({
    mutationFn: (query) => api.post("/patterns/search", query),
  });
}

// ─── Semantic ─────────────────────────────────────────────────────────────────

export function useConceptNet(word: string, enabled = false) {
  return useQuery<ConceptNetResponse>({
    queryKey: ["conceptnet", word],
    queryFn: () => api.get(`/words/${encodeURIComponent(word)}/conceptnet`),
    enabled: enabled && word.length > 0,
    staleTime: 5 * 60_000, // ConceptNet data rarely changes — cache 5 min
  });
}

export function useParaphrase(sentenceId: number, enabled = false) {
  return useQuery<ParaphraseResponse>({
    queryKey: ["paraphrase", sentenceId],
    queryFn: () => api.get(`/sentences/${sentenceId}/paraphrase`),
    enabled: enabled && sentenceId > 0,
  });
}

export function useWordNet(word: string, pos: string, enabled = false) {
  return useQuery<WordNetResponse>({
    queryKey: ["wordnet", word, pos],
    queryFn: () =>
      api.get(`/words/${encodeURIComponent(word)}/wordnet?pos=${encodeURIComponent(pos)}`),
    enabled: enabled && word.length > 0,
    staleTime: 10 * 60_000,
  });
}

export function useAnalyzeSemantics() {
  return useMutation<{ analyzed: boolean; anomaly_count: number }, Error, number>({
    mutationFn: (sentenceId) => api.post(`/sentences/${sentenceId}/analyze`, {}),
  });
}

// Re-export types for convenience
export type { DocumentListItem, SentenceListItem, TokenResponse };
