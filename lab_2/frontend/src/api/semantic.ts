import { useQuery } from "@tanstack/react-query";
import { apiFetch, buildQuery } from "./client";

export interface SemanticResult {
  sentence_id: number;
  text_id: number;
  sentence_index: number;
  content: string;
  similarity: number;
  title: string;
  author: string | null;
  year: number | null;
  genre: string | null;
}

export interface SemanticResponse {
  query: string;
  results: SemanticResult[];
}

export function useSemanticSearch(params: { q: string; limit?: number }) {
  return useQuery<SemanticResponse>({
    queryKey: ["semantic", params],
    queryFn: () => apiFetch(`/semantic/search${buildQuery(params)}`),
    enabled: params.q.length > 0,
  });
}
