import { useQuery } from "@tanstack/react-query";
import { apiFetch, buildQuery } from "./client";

export interface FreqPerText {
  text_id: number;
  title: string;
  author: string | null;
  year: number | null;
  count: number;
  token_count: number;
  relative_freq: number;
}

export interface FrequencyResponse {
  query: string;
  by: string;
  total: number;
  per_text: FreqPerText[];
}

export interface TopNItem {
  term: string;
  count: number;
}

export interface TopNResponse {
  by: string;
  n: number;
  results: TopNItem[];
}

export function useFrequency(params: {
  q: string;
  by?: "surface" | "lemma" | "pos";
  text_id?: number;
}) {
  return useQuery<FrequencyResponse>({
    queryKey: ["frequency", params],
    queryFn: () => apiFetch(`/frequency${buildQuery(params)}`),
    enabled: params.q.length > 0,
  });
}

export function useTopN(params: {
  n?: number;
  by?: "surface" | "lemma" | "pos";
  pos?: string;
  text_id?: number;
  exclude_punct?: boolean;
}) {
  return useQuery<TopNResponse>({
    queryKey: ["topn", params],
    queryFn: () => apiFetch(`/frequency/top${buildQuery(params)}`),
  });
}
