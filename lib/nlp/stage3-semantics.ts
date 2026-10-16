/**
 * Stage 3: Semantic Analysis (NER, SRL Frames, Lesk Word Sense Disambiguation)
 * Extracts named entities, agent-action-patient frames, and disambiguates polysemous words.
 */

import { Entity, SemanticFrame } from "./types";
import { splitSentences, tokenizeSentence, tagPOS } from "./stage2-syntax";

// Target polysemous words for Word Sense Disambiguation
export const TARGET_WSD_WORDS = new Set([
  "bank", "bat", "light", "plant", "spring", "crane", "match", "ring",
]);

interface SynsetDefinition {
  id: string;
  definition: string;
  examples: string[];
  hypernyms: string[];
  keywords: string[];
}

// WordNet synset dictionary for target ambiguous words
const WORDNET_SYNSETS: Record<string, SynsetDefinition[]> = {
  bank: [
    {
      id: "bank.n.01",
      definition: "sloping land (especially the slope beside a body of water)",
      examples: ["they pulled the canoe up on the bank", "the river bank flooded"],
      hypernyms: ["slope", "incline", "geological formation", "land"],
      keywords: ["river", "water", "stream", "mud", "flood", "flooded", "steep", "edge", "lake", "shore", "canoe"],
    },
    {
      id: "bank.n.02",
      definition: "a financial institution that accepts deposits and channels the money into lending activities",
      examples: ["he cashed a check at the bank", "she deposited money in her bank account"],
      hypernyms: ["financial institution", "depository", "organization", "enterprise"],
      keywords: ["money", "deposit", "deposite", "account", "check", "cash", "loan", "lending", "teller", "manager", "closed", "finance", "financial"],
    },
  ],
  bat: [
    {
      id: "bat.n.01",
      definition: "nocturnal mouselike mammal with forelimbs modified to form webbed wings and capable of true flight",
      examples: ["a bat flew around the cavern", "it flew out through the open window"],
      hypernyms: ["mammal", "vertebrate", "animal", "creature"],
      keywords: ["flying", "flew", "fly", "creature", "animal", "nocturnal", "wings", "mammal", "cave", "night", "scared", "cave", "sky"],
    },
    {
      id: "bat.n.02",
      definition: "a club used for hitting the ball in various sports (such as baseball or cricket)",
      examples: ["he swung the baseball bat with both hands"],
      hypernyms: ["club", "implement", "sports equipment"],
      keywords: ["baseball", "cricket", "swung", "hit", "ball", "wooden", "game", "player", "coach", "strike"],
    },
  ],
  light: [
    {
      id: "light.n.01",
      definition: "(physics) electromagnetic radiation that can produce a visual sensation; source of illumination",
      examples: ["the light bulb was flickering in the hallway", "turn on the light"],
      hypernyms: ["radiation", "energy", "illumination", "source"],
      keywords: ["hallway", "bulb", "flickering", "flicker", "lamp", "bright", "brighter", "glow", "shine", "dark", "illumination", "see"],
    },
    {
      id: "light.a.01",
      definition: "of comparatively little physical weight or burdensome density",
      examples: ["a light feather", "the bag was surprisingly light"],
      hypernyms: ["weight", "measurement"],
      keywords: ["weight", "heavy", "carry", "load", "pounds", "kilos", "pack", "bag"],
    },
  ],
  plant: [
    {
      id: "plant.n.01",
      definition: "a living organism of the vegetable kind lacking the power of locomotion",
      examples: ["she watered the house plant in the garden"],
      hypernyms: ["organism", "living thing", "flora"],
      keywords: ["garden", "soil", "water", "flower", "leaf", "leaves", "grow", "green", "botany"],
    },
    {
      id: "plant.n.02",
      definition: "buildings and equipment for manufacturing or power production",
      examples: ["the automobile assembly plant closed down"],
      hypernyms: ["factory", "facility", "building"],
      keywords: ["factory", "manufacturing", "industrial", "power", "workers", "machinery", "production"],
    },
  ],
  match: [
    {
      id: "match.n.01",
      definition: "a formal contest or sports competition between two teams or individuals",
      examples: ["they won the football match yesterday"],
      hypernyms: ["contest", "competition", "game"],
      keywords: ["game", "contest", "tennis", "football", "score", "players", "win", "lost", "tournament"],
    },
    {
      id: "match.n.02",
      definition: "a small wooden or paper stick coated with a substance that ignites when rubbed",
      examples: ["he lit the candle with a match"],
      hypernyms: ["igniter", "device"],
      keywords: ["fire", "candle", "flame", "smoke", "strike", "lit", "burn", "box"],
    },
  ],
  spring: [
    {
      id: "spring.n.01",
      definition: "the season of growth between winter and summer",
      examples: ["flowers bloom during spring"],
      hypernyms: ["season", "time of year"],
      keywords: ["season", "summer", "winter", "autumn", "weather", "bloom", "march", "april", "may"],
    },
    {
      id: "spring.n.02",
      definition: "a natural flow of ground water onto the surface of the earth",
      examples: ["pure mineral spring water"],
      hypernyms: ["water", "source"],
      keywords: ["water", "stream", "drink", "mineral", "source", "well", "flow", "fresh"],
    },
  ],
  crane: [
    {
      id: "crane.n.01",
      definition: "large long-necked wading bird of open marshes and plains",
      examples: ["the whooping crane landed near the lake"],
      hypernyms: ["bird", "wader", "wildlife"],
      keywords: ["bird", "feathers", "wading", "marsh", "lake", "wildlife", "fly", "wings"],
    },
    {
      id: "crane.n.02",
      definition: "large lifting machine with a mechanical boom and cable used in construction",
      examples: ["the crane lifted the steel beam to the roof"],
      hypernyms: ["machine", "construction equipment"],
      keywords: ["construction", "building", "steel", "lift", "operator", "cable", "heavy", "cargo"],
    },
  ],
  ring: [
    {
      id: "ring.n.01",
      definition: "a circular band of precious metal worn around a finger as an ornament",
      examples: ["she wore a diamond engagement ring on her finger"],
      hypernyms: ["jewelry", "band", "ornament"],
      keywords: ["finger", "jewelry", "gold", "silver", "diamond", "wedding", "wear", "worn"],
    },
    {
      id: "ring.n.02",
      definition: "a characteristic resonant sound produced by a bell or telephone",
      examples: ["he waited for the telephone ring"],
      hypernyms: ["sound", "audio"],
      keywords: ["bell", "telephone", "phone", "sound", "hear", "alarm", "tone", "call"],
    },
  ],
};

/**
 * Simplified Lesk algorithm for Word Sense Disambiguation
 */
export function runLeskWSD(word: string, contextTokens: string[]) {
  const lower = word.toLowerCase();
  const synsets = WORDNET_SYNSETS[lower];
  if (!synsets || synsets.length === 0) return null;

  const contextSet = new Set(contextTokens.map((t) => t.toLowerCase()));
  contextSet.delete(lower);

  let bestSynset = synsets[0];
  let maxOverlap = -1;
  let bestOverlapWords: string[] = [];

  for (const syn of synsets) {
    const glossWords = new Set([
      ...syn.definition.toLowerCase().split(/\W+/),
      ...syn.examples.flatMap((e) => e.toLowerCase().split(/\W+/)),
      ...syn.hypernyms.flatMap((h) => h.toLowerCase().split(/\W+/)),
      ...syn.keywords,
    ]);

    const overlapWords: string[] = [];
    for (const token of Array.from(contextSet)) {
      if (glossWords.has(token) && token.length > 2) {
        overlapWords.push(token);
      }
    }

    const score = overlapWords.length;
    if (score > maxOverlap) {
      maxOverlap = score;
      bestSynset = syn;
      bestOverlapWords = overlapWords;
    }
  }

  return {
    synset: bestSynset.id,
    definition: bestSynset.definition,
    hypernyms: bestSynset.hypernyms,
    overlap_score: maxOverlap,
    overlap_words: bestOverlapWords,
  };
}

/**
 * Extract Named Entities (PERSON, ORG, GPE, DATE, etc.)
 */
export function extractNamedEntities(text: string): Entity[] {
  const entities: Entity[] = [];

  // Patterns for NER
  const personPatterns = [
    /\b(Dr\.\s+[A-Z][a-z]+|Professor\s+[A-Z][a-z]+|Prof\.\s+[A-Z][a-z]+)\b/g,
    /\b(Alice|Bob|Sarah|John|Smith|Michael|David|Emma|Mary)\b/g,
  ];

  for (const regex of personPatterns) {
    let match: RegExpExecArray | null;
    while ((match = regex.exec(text)) !== null) {
      entities.push({
        text: match[0],
        label: "PERSON",
        start_char: match.index,
        end_char: match.index + match[0].length,
      });
    }
  }

  // Dates / Days
  const dateRegex = /\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|yesterday|tomorrow|today|last week|next week)\b/gi;
  let dateMatch: RegExpExecArray | null;
  while ((dateMatch = dateRegex.exec(text)) !== null) {
    entities.push({
      text: dateMatch[0],
      label: "DATE",
      start_char: dateMatch.index,
      end_char: dateMatch.index + dateMatch[0].length,
    });
  }

  // Organizations / Products
  const orgRegex = /\b(Google|Microsoft|Apple|OpenAI|Vercel|GitHub|TA)\b/g;
  let orgMatch: RegExpExecArray | null;
  while ((orgMatch = orgRegex.exec(text)) !== null) {
    entities.push({
      text: orgMatch[0],
      label: "ORG",
      start_char: orgMatch.index,
      end_char: orgMatch.index + orgMatch[0].length,
    });
  }

  return entities;
}

/**
 * Extract Semantic Roles (Agent, Action, Patient) for a sentence
 */
export function extractSemanticFrame(sentence: string, fullContextTokens: string[]): SemanticFrame {
  const tokens = tokenizeSentence(sentence);
  const entities = extractNamedEntities(sentence);
  const wordSenses: Record<string, string> = {};
  const wordSensesDetails: SemanticFrame["word_senses_details"] = {};

  // Check for polysemous words
  for (const token of tokens) {
    const lower = token.toLowerCase();
    if (TARGET_WSD_WORDS.has(lower)) {
      const wsdResult = runLeskWSD(lower, fullContextTokens);
      if (wsdResult) {
        wordSenses[lower] = wsdResult.synset;
        wordSensesDetails[lower] = wsdResult;
      }
    }
  }

  // Heuristic extraction for Agent, Action, Patient
  let agent: string | null = null;
  let action: string | null = null;
  let patient: string | null = null;

  // Find action verb
  let actionIdx = -1;
  for (let i = 0; i < tokens.length; i++) {
    const { category } = tagPOS(tokens[i]);
    if (category === "Verb") {
      action = tokens[i];
      actionIdx = i;
      break;
    }
  }

  // Agent: noun or pronoun preceding verb
  if (actionIdx > 0) {
    const candidateTokens: string[] = [];
    for (let i = 0; i < actionIdx; i++) {
      const { category } = tagPOS(tokens[i]);
      if (category === "Noun" || category === "Pronoun" || category === "Determiner") {
        candidateTokens.push(tokens[i]);
      }
    }
    if (candidateTokens.length > 0) {
      agent = candidateTokens.join(" ");
    }
  }

  // Patient: noun or pronoun following verb
  if (actionIdx !== -1 && actionIdx < tokens.length - 1) {
    const patientTokens: string[] = [];
    for (let i = actionIdx + 1; i < tokens.length; i++) {
      const { category, pos } = tagPOS(tokens[i]);
      if (pos === ".") break;
      if (category === "Preposition") break;
      if (category === "Noun" || category === "Pronoun" || category === "Determiner" || category === "Adjective") {
        patientTokens.push(tokens[i]);
      }
    }
    if (patientTokens.length > 0) {
      patient = patientTokens.join(" ");
    }
  }

  return {
    sentence,
    agent,
    action,
    patient,
    entities,
    word_senses: wordSenses,
    word_senses_details: wordSensesDetails,
  };
}

/**
 * Run Stage 3 Semantic Analysis across text
 */
export function analyzeSemantics(text: string): SemanticFrame[] {
  const sentences = splitSentences(text);
  const fullTokens = tokenizeSentence(text);
  return sentences.map((sent) => extractSemanticFrame(sent, fullTokens));
}
