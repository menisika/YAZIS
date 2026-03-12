import { useQuery } from "@tanstack/react-query";
import { apiFetch, buildQuery } from "./client";

export interface ConcordanceLine {
  left: string;
  match: string;
  match_lemma: string;
  match_pos: string;
  right: string;
  text_id: number;
  title: string;
  author: string | null;
  year: number | null;
  genre: string | null;
  sentence_index: number;
  token_index: number;
}

export interface ConcordanceResponse {
  total: number;
  page: number;
  page_size: number;
  results: ConcordanceLine[];
}

export function useConcordance(params: {
  q: string;
  field?: "surface" | "lemma";
  context?: number;
  sort_by?: string;
  page?: number;
  page_size?: number;
  text_id?: number;
}) {
  return useQuery<ConcordanceResponse>({
    queryKey: ["concordance", params],
    queryFn: () => apiFetch(`/search${buildQuery(params)}`),
    enabled: params.q.length > 0,
  });
}
