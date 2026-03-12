import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, buildQuery } from "./client";

export interface TextSummary {
  id: number;
  title: string;
  author: string | null;
  year: number | null;
  genre: string | null;
  source_url: string | null;
  token_count: number;
  sentence_count: number;
  created_at: string | null;
}

export interface TextsResponse {
  total: number;
  page: number;
  page_size: number;
  results: TextSummary[];
}

export interface AnnotatedToken {
  surface: string;
  lemma: string;
  pos: string;
  tag: string;
  morph: Record<string, string[]> | null;
  sentence_index: number;
  token_index: number;
  char_start: number;
  char_end: number;
}

export interface AnnotatedContent {
  text_id: number;
  title: string;
  total_tokens: number;
  page: number;
  page_size: number;
  tokens: AnnotatedToken[];
}

export function useTexts(params: {
  search?: string;
  genre?: string;
  author?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery<TextsResponse>({
    queryKey: ["texts", params],
    queryFn: () => apiFetch(`/texts${buildQuery(params)}`),
  });
}

export function useText(id: number) {
  return useQuery<TextSummary>({
    queryKey: ["text", id],
    queryFn: () => apiFetch(`/texts/${id}`),
    enabled: !!id,
  });
}

export function useAnnotatedContent(id: number, page: number, pageSize = 500) {
  return useQuery<AnnotatedContent>({
    queryKey: ["annotated", id, page],
    queryFn: () => apiFetch(`/texts/${id}/content${buildQuery({ page, page_size: pageSize })}`),
    enabled: !!id,
  });
}

export function useDeleteText() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiFetch(`/texts/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["texts"] }),
  });
}
