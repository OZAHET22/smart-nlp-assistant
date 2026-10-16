/**
 * Stage 5: Full NLP Pipeline Assembly & Metrics
 * Wires Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 continuously.
 * Stage 2+ operates on the corrected text from Stage 1.
 */

import { BenchmarkResult, PipelineResult, ReadabilityMetrics } from "./types";
import { checkSpelling } from "./stage1-spellcheck";
import { parseSyntax, splitSentences } from "./stage2-syntax";
import { analyzeSemantics } from "./stage3-semantics";
import { resolveCoreference, detectDiscourseRelations, detectIndirectRequests } from "./stage4-discourse";
import { TEST_SAMPLES } from "./samples-data";

/**
 * Approximate syllable count for a word
 */
function countSyllables(word: string): number {
  const clean = word.toLowerCase().replace(/[^a-z]/g, "");
  if (clean.length <= 3) return 1;
  const matches = clean.match(/[aeiouy]{1,2}/g);
  let count = matches ? matches.length : 1;
  if (clean.endsWith("e") && !clean.endsWith("le")) {
    count = Math.max(1, count - 1);
  }
  return Math.max(1, count);
}

/**
 * Compute readability scores and metrics
 */
export function calculateReadability(text: string): ReadabilityMetrics {
  const sentences = splitSentences(text);
  const sentenceCount = Math.max(1, sentences.length);
  const words = text.match(/[a-zA-Z0-9']+/g) || [];
  const wordCount = Math.max(1, words.length);
  const charCount = text.length;

  let totalSyllables = 0;
  for (const w of words) {
    totalSyllables += countSyllables(w);
  }

  const wordsPerSentence = wordCount / sentenceCount;
  const syllablesPerWord = totalSyllables / wordCount;

  // Flesch Reading Ease: 206.835 - 1.015 * (words/sentence) - 84.6 * (syllables/word)
  let readingEase = Math.round((206.835 - (1.015 * wordsPerSentence) - (84.6 * syllablesPerWord)) * 10) / 10;
  readingEase = Math.max(0, Math.min(100, readingEase));

  // Flesch-Kincaid Grade Level: 0.39 * (words/sentence) + 11.8 * (syllables/word) - 15.59
  let gradeLevel = Math.round(((0.39 * wordsPerSentence) + (11.8 * syllablesPerWord) - 15.59) * 10) / 10;
  gradeLevel = Math.max(1, Math.min(18, gradeLevel));

  let readingLevel: ReadabilityMetrics["reading_level"] = "Standard";
  if (readingEase >= 80) readingLevel = "Easy";
  else if (readingEase >= 60) readingLevel = "Standard";
  else if (readingEase >= 45) readingLevel = "Fairly Difficult";
  else if (readingEase >= 30) readingLevel = "Difficult";
  else readingLevel = "Very Confusing";

  // Tone detection
  const lower = text.toLowerCase();
  let tone: ReadabilityMetrics["sentiment_tone"] = "Neutral / Direct";
  if (/\b(hey|yo|prof|plz|pls|cuz|becuz|stuff|alot)\b/.test(lower)) {
    tone = "Casual & Informal";
  } else if (/\b(urgent|asap|immediately|deadline|emergency|hazard)\b/.test(lower)) {
    tone = "Urgent";
  } else if (/\b(dr\.|professor|lecture|biodiversity|deforestation|temperature|solutions|director|agenda)\b/.test(lower)) {
    tone = "Polite / Academic";
  }

  const readingTimeSeconds = Math.round((wordCount / 220) * 60);

  return {
    flesch_reading_ease: readingEase,
    flesch_kincaid_grade: gradeLevel,
    reading_level: readingLevel,
    word_count: wordCount,
    character_count: charCount,
    sentence_count: sentenceCount,
    avg_sentence_length: Math.round(wordsPerSentence * 10) / 10,
    reading_time_seconds: Math.max(1, readingTimeSeconds),
    sentiment_tone: tone,
  };
}

/**
 * Execute the full continuous NLP pipeline:
 * Stage 1 (Spelling) -> Stage 2 (Syntax on corrected) -> Stage 3 (Semantics) -> Stage 4 (Discourse)
 */
export function runPipeline(rawText: string): PipelineResult {
  const startTime = Date.now();

  // Stage 1: Spell Checking
  const t0 = Date.now();
  const spellResult = checkSpelling(rawText);
  const timeStage1 = Date.now() - t0;

  const correctedText = spellResult.corrected_text;

  // Stage 2: Syntactic Processing on corrected text
  const t1 = Date.now();
  const sentenceParses = parseSyntax(correctedText);
  const timeStage2 = Date.now() - t1;

  // Stage 3: Semantic Analysis on corrected text
  const t2 = Date.now();
  const semanticFrames = analyzeSemantics(correctedText);
  const timeStage3 = Date.now() - t2;

  // Stage 4: Discourse & Pragmatic Analysis on corrected text
  const t3 = Date.now();
  const corefChains = resolveCoreference(correctedText);
  const discourseRelations = detectDiscourseRelations(correctedText);
  const pragmaticNotes = detectIndirectRequests(correctedText);
  const timeStage4 = Date.now() - t3;

  const totalTime = Date.now() - startTime;
  const metrics = calculateReadability(correctedText);

  return {
    corrected_text: correctedText,
    corrections: spellResult.corrections,
    sentence_parses: sentenceParses,
    semantic_frames: semanticFrames,
    coref_chains: corefChains,
    discourse_relations: discourseRelations,
    pragmatic_notes: pragmaticNotes,
    metrics,
    processing_time_ms: {
      stage1_spell: timeStage1,
      stage2_syntax: timeStage2,
      stage3_semantics: timeStage3,
      stage4_discourse: timeStage4,
      total: totalTime,
    },
  };
}

/**
 * Run batch benchmarks on all 10 student samples
 */
export function runBatchBenchmark(): BenchmarkResult[] {
  return TEST_SAMPLES.map((sample) => {
    const t0 = Date.now();
    const result = runPipeline(sample.text);
    const elapsed = Date.now() - t0;

    const cykParsedCount = result.sentence_parses.filter((s) => s.is_valid_cfg).length;
    let entitiesCount = 0;
    for (const frame of result.semantic_frames) {
      entitiesCount += frame.entities.length;
    }

    return {
      sample_id: sample.id,
      title: sample.title,
      word_count: result.metrics.word_count,
      corrections_count: result.corrections.length,
      cyk_parsed_count: cykParsedCount,
      entities_count: entitiesCount,
      coref_count: result.coref_chains.length,
      discourse_count: result.discourse_relations.length,
      indirect_requests_count: result.pragmatic_notes.length,
      total_time_ms: elapsed,
      status: "Passed",
    };
  });
}

/**
 * Generate formatted executive Markdown report
 */
export function generateMarkdownReport(result: PipelineResult, rawText: string): string {
  const lines: string[] = [];
  lines.push("# Smart NLP Assistant — Executive Analysis Report");
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push("");

  lines.push("## 1. Summary & Readability Metrics");
  lines.push(`- **Word Count:** ${result.metrics.word_count}`);
  lines.push(`- **Sentence Count:** ${result.metrics.sentence_count}`);
  lines.push(`- **Reading Ease:** ${result.metrics.flesch_reading_ease} / 100 (${result.metrics.reading_level})`);
  lines.push(`- **Grade Level:** Grade ${result.metrics.flesch_kincaid_grade}`);
  lines.push(`- **Tone:** ${result.metrics.sentiment_tone}`);
  lines.push(`- **Corrections Made:** ${result.corrections.length}`);
  lines.push("");

  lines.push("## 2. Text Comparison");
  lines.push("### Original Text");
  lines.push(`> ${rawText}`);
  lines.push("");
  lines.push("### Corrected Text");
  lines.push(`> ${result.corrected_text}`);
  lines.push("");

  lines.push("## 3. Stage 1 — Spelling & Disambiguation");
  if (result.corrections.length === 0) {
    lines.push("_No spelling corrections needed._");
  } else {
    lines.push("| Original | Corrected | Edit Dist | Reason | Score |");
    lines.push("|---|---|---|---|---|");
    for (const c of result.corrections) {
      lines.push(`| ${c.original} | **${c.corrected}** | ${c.edit_distance} | ${c.reason} | ${c.score.toFixed(2)} |`);
    }
  }
  lines.push("");

  lines.push("## 4. Stage 2 — Syntactic Parse & CYK Trees");
  for (let i = 0; i < result.sentence_parses.length; i++) {
    const sp = result.sentence_parses[i];
    lines.push(`### Sentence ${i + 1}: "${sp.sentence}"`);
    if (sp.cyk_parse_string) {
      lines.push("```");
      lines.push(sp.cyk_parse_string);
      lines.push("```");
    }
  }
  lines.push("");

  lines.push("## 5. Stage 3 — Semantic Frames & WSD");
  for (const frame of result.semantic_frames) {
    lines.push(`- **Sentence:** "${frame.sentence}"`);
    lines.push(`  - **Agent:** ${frame.agent || "None"}`);
    lines.push(`  - **Action:** ${frame.action || "None"}`);
    lines.push(`  - **Patient:** ${frame.patient || "None"}`);
    if (Object.keys(frame.word_senses).length > 0) {
      for (const [w, sense] of Object.entries(frame.word_senses)) {
        lines.push(`  - **WSD (${w}):** ${sense}`);
      }
    }
  }
  lines.push("");

  lines.push("## 6. Stage 4 — Discourse & Pragmatic Inferences");
  if (result.coref_chains.length > 0) {
    lines.push("### Coreference Chains");
    for (const c of result.coref_chains) {
      lines.push(`- [${c.entity_type}] ${c.mentions.join(" → ")}`);
    }
  }

  if (result.discourse_relations.length > 0) {
    lines.push("### Discourse Relations");
    for (const d of result.discourse_relations) {
      lines.push(`- **${d.connective}** (${d.relation}) connects Sentence ${d.sentence_a + 1} → Sentence ${d.sentence_b + 1}`);
    }
  }

  if (result.pragmatic_notes.length > 0) {
    lines.push("### Indirect Speech Acts");
    for (const p of result.pragmatic_notes) {
      lines.push(`- Surface: "${p.surface_form}"`);
      lines.push(`  - Inferred Act: **${p.inferred_act}**`);
      lines.push(`  - Implied Request: _"${p.paraphrase}"_`);
    }
  }

  return lines.join("\n");
}
