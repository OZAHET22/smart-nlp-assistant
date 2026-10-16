/**
 * Core type definitions for Smart Reading & Writing Assistant (Enterprise NLP Studio)
 * Matches the pipeline stages 1-5 specifications.
 */

export interface SpellCorrection {
  original: string;
  corrected: string;
  edit_distance: number;
  reason: "edit_distance" | "context_ngram" | "unchanged";
  score: number;
  context_score: number;
  candidate_alternatives?: Array<{ word: string; dist: number; score: number }>;
}

export interface SpellCheckResult {
  original_text: string;
  corrected_text: string;
  corrections: SpellCorrection[];
}

export interface TokenAnalysis {
  text: string;
  pos: string;
  pos_category: "Noun" | "Verb" | "Adjective" | "Pronoun" | "Determiner" | "Preposition" | "Adverb" | "Conjunction" | "Modal" | "Punctuation" | "Other";
  dep: string;
  head: string;
}

export interface ParseTreeNode {
  label: string;
  children?: ParseTreeNode[];
  text?: string;
}

export interface SentenceParse {
  sentence: string;
  tokens: TokenAnalysis[];
  custom_parse_tree: ParseTreeNode | null;
  cyk_parse_string?: string;
  is_valid_cfg?: boolean;
}

export interface Entity {
  text: string;
  label: "PERSON" | "ORG" | "GPE" | "DATE" | "MONEY" | "TIME" | "EVENT" | "FAC" | "NORP" | "PRODUCT";
  start_char: number;
  end_char: number;
}

export interface SemanticFrame {
  sentence: string;
  agent: string | null;
  action: string | null;
  patient: string | null;
  entities: Entity[];
  word_senses: Record<string, string>;
  word_senses_details?: Record<string, {
    synset: string;
    definition: string;
    hypernyms: string[];
    overlap_score: number;
    overlap_words: string[];
  }>;
}

export interface CorefChain {
  mentions: string[];
  entity_type: "PERSON" | "OBJECT" | "UNKNOWN";
  gender_agreement?: "male" | "female" | "neutral" | "plural" | "unknown";
}

export interface DiscourseRelation {
  connective: string;
  relation: "contrast" | "cause" | "cause_effect" | "elaboration" | "temporal" | "condition";
  sentence_a: number;
  sentence_b: number;
  context_snippet?: string;
}

export interface PragmaticNote {
  surface_form: string;
  inferred_act: "indirect_request" | "polite_request" | "hedged_assertion";
  paraphrase: string;
  intent_confidence?: number;
}

export interface ReadabilityMetrics {
  flesch_reading_ease: number;
  flesch_kincaid_grade: number;
  reading_level: "Easy" | "Standard" | "Fairly Difficult" | "Difficult" | "Very Confusing";
  word_count: number;
  character_count: number;
  sentence_count: number;
  avg_sentence_length: number;
  reading_time_seconds: number;
  sentiment_tone: "Casual & Informal" | "Neutral / Direct" | "Polite / Academic" | "Urgent";
}

export interface PipelineResult {
  corrected_text: string;
  corrections: SpellCorrection[];
  sentence_parses: SentenceParse[];
  semantic_frames: SemanticFrame[];
  coref_chains: CorefChain[];
  discourse_relations: DiscourseRelation[];
  pragmatic_notes: PragmaticNote[];
  metrics: ReadabilityMetrics;
  processing_time_ms: {
    stage1_spell: number;
    stage2_syntax: number;
    stage3_semantics: number;
    stage4_discourse: number;
    total: number;
  };
}

export interface LevenshteinMatrixResult {
  word1: string;
  word2: string;
  distance: number;
  matrix: number[][];
  operations: Array<{
    type: "match" | "substitute" | "insert" | "delete";
    char1?: string;
    char2?: string;
    cost: number;
  }>;
}

export interface TestSample {
  id: string;
  filename: string;
  title: string;
  description: string;
  text: string;
  expected_features: string[];
}

export interface BenchmarkResult {
  sample_id: string;
  title: string;
  word_count: number;
  corrections_count: number;
  cyk_parsed_count: number;
  entities_count: number;
  coref_count: number;
  discourse_count: number;
  indirect_requests_count: number;
  total_time_ms: number;
  status: "Passed" | "Warning" | "Error";
}
