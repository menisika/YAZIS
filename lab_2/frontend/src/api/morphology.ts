import { useQuery } from "@tanstack/react-query";
import { apiFetch, buildQuery } from "./client";

export interface MorphForm {
  surface: string;
  pos: string;
  tag: string;
  morph: Record<string, string[]>;
  count: number;
  examples: string[];
}

export interface GrammarCard {
  lemma: string;
  total_occurrences: number;
  forms: MorphForm[];
}

export function useGrammarCard(lemma: string, textId?: number) {
  return useQuery<GrammarCard>({
    queryKey: ["morphology", lemma, textId],
    queryFn: () => apiFetch(`/morphology/${encodeURIComponent(lemma)}${buildQuery({ text_id: textId })}`),
    enabled: lemma.length > 0,
  });
}
