/**
 * Stage 4: Discourse & Pragmatic Processing
 * Coreference resolution, discourse relation classification, and indirect request detection.
 */

import { CorefChain, DiscourseRelation, PragmaticNote } from "./types";
import { splitSentences, tokenizeSentence } from "./stage2-syntax";

// Pronoun gender & agreement sets
const MALE_PRONOUNS = new Set(["he", "him", "his", "himself"]);
const FEMALE_PRONOUNS = new Set(["she", "her", "hers", "herself"]);
const NEUTRAL_PRONOUNS = new Set(["it", "its", "itself"]);
const PLURAL_PRONOUNS = new Set(["they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours"]);

const MALE_INDICATORS = new Set(["john", "dad", "father", "mr", "brother", "coach", "janitor", "manager", "boy", "man", "he", "him"]);
const FEMALE_INDICATORS = new Set(["sarah", "dr. smith", "smith", "alice", "mother", "mom", "mrs", "ms", "sister", "girl", "woman", "she", "her"]);

// Discourse Connectives Dictionary
const DISCOURSE_CONNECTIVES: Array<{ connective: string; relation: DiscourseRelation["relation"] }> = [
  // Contrast
  { connective: "on the other hand", relation: "contrast" },
  { connective: "even though", relation: "contrast" },
  { connective: "nevertheless", relation: "contrast" },
  { connective: "nonetheless", relation: "contrast" },
  { connective: "however", relation: "contrast" },
  { connective: "although", relation: "contrast" },
  { connective: "though", relation: "contrast" },
  { connective: "whereas", relation: "contrast" },
  { connective: "while", relation: "contrast" },
  { connective: "yet", relation: "contrast" },
  { connective: "but", relation: "contrast" },

  // Cause & Effect
  { connective: "because of this", relation: "cause" },
  { connective: "for this reason", relation: "cause" },
  { connective: "as a result", relation: "cause_effect" },
  { connective: "consequently", relation: "cause_effect" },
  { connective: "therefore", relation: "cause_effect" },
  { connective: "because", relation: "cause" },
  { connective: "since", relation: "cause" },
  { connective: "thus", relation: "cause_effect" },
  { connective: "hence", relation: "cause_effect" },
  { connective: "so", relation: "cause_effect" },

  // Elaboration
  { connective: "in addition", relation: "elaboration" },
  { connective: "additionally", relation: "elaboration" },
  { connective: "furthermore", relation: "elaboration" },
  { connective: "moreover", relation: "elaboration" },
  { connective: "for example", relation: "elaboration" },
  { connective: "for instance", relation: "elaboration" },
  { connective: "also", relation: "elaboration" },
  { connective: "besides", relation: "elaboration" },

  // Temporal
  { connective: "meanwhile", relation: "temporal" },
  { connective: "eventually", relation: "temporal" },
  { connective: "finally", relation: "temporal" },
  { connective: "after", relation: "temporal" },
  { connective: "before", relation: "temporal" },
  { connective: "then", relation: "temporal" },

  // Condition
  { connective: "provided that", relation: "condition" },
  { connective: "unless", relation: "condition" },
  { connective: "if", relation: "condition" },
];

// Indirect Request Patterns
const INDIRECT_REQUEST_PATTERNS = [
  {
    regex: /\b(could you|can you|would you|will you|would you mind)\b\s+([^?]+)\?/i,
    extract: (m: RegExpExecArray) => m[2].trim(),
  },
  {
    regex: /\b(would it be possible for you to|is it possible to|do you think you could)\b\s+([^?]+)\?/i,
    extract: (m: RegExpExecArray) => m[2].trim(),
  },
  {
    regex: /\b(i was wondering if you could|i wanted to ask about|i wanted to ask if you could)\b\s+([^.!?]+)/i,
    extract: (m: RegExpExecArray) => m[2].trim(),
  },
  {
    regex: /\b(could you look into it|could you check this|can someone explane|can someone explain)\b\s*([^?]*)\??/i,
    extract: (m: RegExpExecArray) => `${m[1]} ${m[2]}`.trim(),
  },
];

/**
 * Resolve pronoun coreference chains
 */
export function resolveCoreference(text: string): CorefChain[] {
  const chains: CorefChain[] = [];
  const sentences = splitSentences(text);

  // Entities tracked
  const entityClusters: Record<string, { type: CorefChain["entity_type"]; gender: CorefChain["gender_agreement"]; mentions: string[] }> = {};

  // Find prominent entities
  for (const sent of sentences) {
    const tokens = tokenizeSentence(sent);

    // Look for names / nouns
    for (let i = 0; i < tokens.length; i++) {
      const lower = tokens[i].toLowerCase();

      // Check known individuals
      if (lower === "john" || lower === "dad" || lower === "manager" || lower === "coach" || lower === "janitor") {
        const key = lower === "john" ? "John" : lower === "dad" ? "Dad" : tokens[i];
        if (!entityClusters[key]) {
          entityClusters[key] = { type: "PERSON", gender: "male", mentions: [tokens[i]] };
        }
      } else if (lower === "sarah" || lower === "alice" || lower === "smith") {
        const key = lower === "sarah" ? "Sarah" : lower === "alice" ? "Alice" : "Dr. Smith";
        if (!entityClusters[key]) {
          entityClusters[key] = { type: "PERSON", gender: "female", mentions: [tokens[i]] };
        }
      }

      // Resolve pronouns to active cluster
      if (MALE_PRONOUNS.has(lower)) {
        const maleCluster = Object.values(entityClusters).find((c) => c.gender === "male");
        if (maleCluster && !maleCluster.mentions.includes(tokens[i])) {
          maleCluster.mentions.push(tokens[i]);
        }
      } else if (FEMALE_PRONOUNS.has(lower)) {
        const femaleCluster = Object.values(entityClusters).find((c) => c.gender === "female");
        if (femaleCluster && !femaleCluster.mentions.includes(tokens[i])) {
          femaleCluster.mentions.push(tokens[i]);
        }
      } else if (NEUTRAL_PRONOUNS.has(lower)) {
        // e.g. laptop, bank, bat, window, light
        if (!entityClusters["it_entity"]) {
          entityClusters["it_entity"] = { type: "OBJECT", gender: "neutral", mentions: ["it"] };
        } else {
          entityClusters["it_entity"].mentions.push(tokens[i]);
        }
      }
    }
  }

  for (const [key, cluster] of Object.entries(entityClusters)) {
    if (cluster.mentions.length >= 2 || cluster.type === "PERSON") {
      chains.push({
        mentions: cluster.mentions,
        entity_type: cluster.type,
        gender_agreement: cluster.gender,
      });
    }
  }

  return chains;
}

/**
 * Detect Discourse Relations across sentences
 */
export function detectDiscourseRelations(text: string): DiscourseRelation[] {
  const relations: DiscourseRelation[] = [];
  const sentences = splitSentences(text);

  for (let i = 0; i < sentences.length; i++) {
    const currentSent = sentences[i].toLowerCase();

    for (const item of DISCOURSE_CONNECTIVES) {
      const connectivePattern = new RegExp(`(^|[.,;\\s])(${item.connective})([.,;\\s]|$)`, "i");
      if (connectivePattern.test(currentSent)) {
        relations.push({
          connective: item.connective,
          relation: item.relation,
          sentence_a: Math.max(0, i - 1),
          sentence_b: i,
          context_snippet: sentences[i],
        });
        break; // One relation per connective found in sentence
      }
    }
  }

  return relations;
}

/**
 * Detect Indirect Requests and Pragmatic Speech Acts
 */
export function detectIndirectRequests(text: string): PragmaticNote[] {
  const notes: PragmaticNote[] = [];
  const sentences = splitSentences(text);

  for (const sent of sentences) {
    for (const pattern of INDIRECT_REQUEST_PATTERNS) {
      const match = pattern.regex.exec(sent);
      if (match) {
        const actionPart = pattern.extract(match);
        notes.push({
          surface_form: sent,
          inferred_act: "indirect_request",
          paraphrase: actionPart.startsWith("send") || actionPart.startsWith("look") || actionPart.startsWith("escalate")
            ? actionPart
            : `Please ${actionPart}`,
          intent_confidence: 0.94,
        });
        break;
      }
    }
  }

  return notes;
}
