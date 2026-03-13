export interface DocumentListItem {
  id: number;
  filename: string;
  original_format: string;
  uploaded_at: string;
  word_count: number;
  sentence_count: number;
  avg_complexity: number;
  total_tokens: number;
}

export interface DocumentResponse {
  id: number;
  filename: string;
  original_format: string;
  uploaded_at: string;
  word_count: number;
  sentence_count: number;
}

export interface DocumentsPage {
  total: number;
  items: DocumentListItem[];
}

export interface SentenceListItem {
  id: number;
  document_id: number;
  index: number;
  text: string;
  complexity_score: number;
  token_count: number;
}

export interface SentencesPage {
  total: number;
  items: SentenceListItem[];
}

export interface TokenResponse {
  id: number;
  sentence_id: number;
  index: number;
  text: string;
  lemma: string;
  pos: string;
  tag: string;
  dep: string;
  head_index: number;
  is_stop: boolean;
  is_punct: boolean;
  ent_type: string;
}

export interface SentenceResponse extends SentenceListItem {
  tokens: TokenResponse[];
}

export interface ProcessingSummary {
  document_id: number;
  filename: string;
  sentence_count: number;
  token_count: number;
  parse_duration_ms: number;
}

export interface PatternQuery {
  source_pos: string;
  dep_rel: string;
  target_pos: string;
}

export interface PatternMatch {
  sentence: SentenceListItem;
  source_token_index: number;
  target_token_index: number;
  source_text: string;
  target_text: string;
}

export interface PatternSearchResponse {
  query: PatternQuery;
  total: number;
  matches: PatternMatch[];
}
