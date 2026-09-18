"""
Full NLP pipeline — Stage 1 → Stage 2 → Stage 3 → Stage 4.

Provides ``process(raw_text) -> PipelineResult`` and a CLI entry point::

    python pipeline.py --input data/test_samples/sample_01.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

# Ensure the project root is on sys.path so stage imports work when run as
# ``python pipeline.py`` from the project root.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from nltk.tokenize import sent_tokenize

from stage1_spellcheck.spellchecker import SpellChecker, SpellCorrection, SpellCheckResult
from stage2_syntax.dependency_parser import dependency_parse, SentenceParse, TokenAnalysis
from stage2_syntax.cyk_parser import CYKParser, build_parse_tree_string
from stage3_semantics.ner import Entity, extract_entities
from stage3_semantics.srl import SemanticFrame, extract_semantic_roles, semantic_analysis
from stage3_semantics.wsd import disambiguate
from stage4_discourse.coref import CorefChain, resolve_coreference
from stage4_discourse.discourse_relations import DiscourseRelation, detect_discourse_relations
from stage4_discourse.pragmatics import PragmaticNote, detect_indirect_requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclass
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Aggregated result from all four pipeline stages."""
    corrected_text: str
    corrections: list[SpellCorrection]
    sentence_parses: list[SentenceParse]
    semantic_frames: list[SemanticFrame]
    coref_chains: list[CorefChain]
    discourse_relations: list[DiscourseRelation]
    pragmatic_notes: list[PragmaticNote]


# ---------------------------------------------------------------------------
# Singletons (expensive to initialise, reuse across calls)
# ---------------------------------------------------------------------------

_spell_checker: SpellChecker | None = None
_cyk_parser: CYKParser | None = None


def _get_spell_checker() -> SpellChecker:
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = SpellChecker()
    return _spell_checker


def _get_cyk_parser() -> CYKParser:
    global _cyk_parser
    if _cyk_parser is None:
        _cyk_parser = CYKParser()
    return _cyk_parser


# ---------------------------------------------------------------------------
# Core pipeline function (spec-required signature)
# ---------------------------------------------------------------------------

def process(raw_text: str) -> PipelineResult:
    """Run the full NLP pipeline on *raw_text*.

    Stage 1 → Stage 2 → Stage 3 → Stage 4, in that order.
    Stage 2+ runs on the *corrected* text from Stage 1, not the raw input,
    so downstream parses/semantics are scored against clean text.

    Parameters
    ----------
    raw_text : str
        Raw, potentially messy input text.

    Returns
    -------
    PipelineResult
    """
    t_total = time.perf_counter()

    # ── Stage 1: Spell Checking ──────────────────────────────────────────
    t0 = time.perf_counter()
    sc = _get_spell_checker()
    spell_result: SpellCheckResult = sc.correct(raw_text)
    corrected_text = spell_result.corrected_text
    corrections = spell_result.corrections
    logger.info("Stage 1 done: %d corrections (%.3fs)",
                 len(corrections), time.perf_counter() - t0)

    # ── Stage 2: Syntactic Processing ────────────────────────────────────
    t0 = time.perf_counter()
    sentence_parses: list[SentenceParse] = dependency_parse(corrected_text)

    cyk = _get_cyk_parser()
    sentences = sent_tokenize(corrected_text)
    for i, sent in enumerate(sentences):
        if i < len(sentence_parses):
            tree, _tagged = cyk.parse(sent)
            sentence_parses[i].custom_parse_tree = tree
    logger.info("Stage 2 done: %d sentences parsed (%.3fs)",
                 len(sentence_parses), time.perf_counter() - t0)

    # ── Stage 3: Semantic Analysis ───────────────────────────────────────
    t0 = time.perf_counter()
    semantic_frames: list[SemanticFrame] = []
    for sent in sentences:
        frame = semantic_analysis(sent)
        semantic_frames.append(frame)
    logger.info("Stage 3 done: %d frames (%.3fs)",
                 len(semantic_frames), time.perf_counter() - t0)

    # ── Stage 4: Discourse & Pragmatics ──────────────────────────────────
    t0 = time.perf_counter()
    coref_chains = resolve_coreference(corrected_text)
    discourse_relations = detect_discourse_relations(corrected_text)
    pragmatic_notes = detect_indirect_requests(corrected_text)
    logger.info("Stage 4 done: %d coref, %d discourse, %d pragmatic (%.3fs)",
                 len(coref_chains), len(discourse_relations),
                 len(pragmatic_notes), time.perf_counter() - t0)

    logger.info("Pipeline total: %.3fs", time.perf_counter() - t_total)

    return PipelineResult(
        corrected_text=corrected_text,
        corrections=corrections,
        sentence_parses=sentence_parses,
        semantic_frames=semantic_frames,
        coref_chains=coref_chains,
        discourse_relations=discourse_relations,
        pragmatic_notes=pragmatic_notes,
    )


# ---------------------------------------------------------------------------
# Pretty-print helper
# ---------------------------------------------------------------------------

def print_results(result: PipelineResult, raw_text: str = "") -> None:
    """Print a human-readable summary of a PipelineResult."""
    print("=" * 70)
    if raw_text:
        print("ORIGINAL TEXT:")
        print(raw_text)
        print()

    if result.corrections:
        print("SPELLING CORRECTIONS:")
        for c in result.corrections:
            print(f"  {c.original} -> {c.corrected}  "
                  f"(edit_dist={c.edit_distance}, {c.reason}, score={c.score:.4f})")
        print()
        print("CORRECTED TEXT:")
        print(result.corrected_text)
        print()
    else:
        print("No spelling corrections needed.\n")

    print("PARSE TREES (CYK):")
    for sp in result.sentence_parses:
        sent_text = " ".join(t.text for t in sp.tokens)
        print(f"  Sentence: {sent_text}")
        print(f"  Tree:")
        tree_str = build_parse_tree_string(sp.custom_parse_tree)
        for line in tree_str.split("\n"):
            print(f"    {line}")
        print()

    if result.semantic_frames:
        print("SEMANTIC FRAMES:")
        for f in result.semantic_frames:
            agent = f.agent or "(none)"
            patient = f.patient or "(none)"
            print(f"  {f.sentence[:50]:50s}")
            print(f"    agent: {agent}, action: {f.action}, patient: {patient}")
            if f.word_senses:
                for w, s in f.word_senses.items():
                    print(f"    WSD: {w} -> {s}")
        print()

    if result.coref_chains:
        print("COREFERENCE CHAINS:")
        for chain in result.coref_chains:
            print(f"  [{chain.entity_type}] {' -> '.join(chain.mentions)}")
        print()

    if result.discourse_relations:
        print("DISCOURSE RELATIONS:")
        for r in result.discourse_relations:
            print(f"  [{r.relation:12s}] '{r.connective}' "
                  f"(sent {r.sentence_a} -> {r.sentence_b})")
        print()

    if result.pragmatic_notes:
        print("INDIRECT REQUESTS:")
        for n in result.pragmatic_notes:
            print(f"  [{n.inferred_act}] {n.surface_form[:60]}")
            print(f"    -> {n.paraphrase}")
        print()

    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: ``python pipeline.py --input data/test_samples/sample_01.txt``"""
    parser = argparse.ArgumentParser(
        description="Smart Reading & Writing Assistant — NLP Pipeline",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to a text file to process",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output structured JSON instead of human-readable text",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    with open(args.input, encoding="utf-8") as fh:
        raw_text = fh.read().strip()

    result = process(raw_text)

    if args.json:
        # Convert dataclasses to dicts for JSON serialisation
        out = asdict(result)
        print(json.dumps(out, indent=2, default=str))
    else:
        print_results(result, raw_text)


if __name__ == "__main__":
    main()
