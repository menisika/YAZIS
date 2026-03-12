import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";

export interface StyleMetrics {
  ttr: number;
  mtld: number;
  avg_sentence_length: number;
  lexical_density: number;
  flesch_kincaid: number;
}

export interface POSDistribution {
  NOUN: number;
  VERB: number;
  ADJ: number;
  ADV: number;
  OTHER: number;
}

export interface TopLemma {
  lemma: string;
  count: number;
}

export interface DistinctiveWord {
  lemma: string;
  score: number;
}

export interface TextStyle {
  text_id: number;
  title: string;
  author: string | null;
  year: number | null;
  genre: string | null;
  token_count: number;
  sentence_count: number;
  metrics: StyleMetrics;
  pos_distribution: POSDistribution;
  top_content_lemmas: TopLemma[];
  distinctive_words?: DistinctiveWord[];
}

export interface CompareResponse {
  texts: TextStyle[];
}

export function useTextStyle(textId: number) {
  return useQuery<TextStyle>({
    queryKey: ["style", textId],
    queryFn: () => apiFetch(`/style/texts/${textId}`),
    enabled: !!textId,
  });
}

export function useCompareTexts(textIds: number[]) {
  return useQuery<CompareResponse>({
    queryKey: ["style-compare", textIds],
    queryFn: () => apiFetch(`/style/compare?text_ids=${textIds.join(",")}`),
    enabled: textIds.length >= 2,
  });
}
