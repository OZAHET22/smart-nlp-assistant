"""
Dependency parser — library-backed via spaCy (with NLTK fallback).

Returns spec-compliant :class:`TokenAnalysis` and :class:`SentenceParse`
dataclasses.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from nltk.tokenize import sent_tokenize, word_tokenize

try:
    from utils import get_spacy
except ImportError:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from utils import get_spacy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TokenAnalysis:
    """POS and dependency information for a single token."""
    text: str
    pos: str
    dep: str
    head: str


@dataclass
class SentenceParse:
    """Parse result for a single sentence, combining library-based and
    custom parser outputs."""
    tokens: list[TokenAnalysis]
    custom_parse_tree: Any | None = None   # ParseTree from CYK, None if out-of-grammar


# ---------------------------------------------------------------------------
# spaCy singleton
# ---------------------------------------------------------------------------

def _dependency_parse_spacy(sentence: str) -> list[TokenAnalysis]:
    """Parse a single sentence with spaCy."""
    nlp = get_spacy()
    if not nlp:
        return _dependency_parse_fallback(sentence)
    doc = nlp(sentence)
    return [
        TokenAnalysis(
            text=tok.text,
            pos=tok.pos_,
            dep=tok.dep_,
            head=tok.head.text,
        )
        for tok in doc
    ]


def _dependency_parse_fallback(sentence: str) -> list[TokenAnalysis]:
    """Fallback parse using NLTK POS tags (no real dep info)."""
    from nltk import pos_tag
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    return [
        TokenAnalysis(text=w, pos=tag, dep="unknown", head=w)
        for w, tag in tagged
    ]


# ---------------------------------------------------------------------------
# Public API (spec-required signature)
# ---------------------------------------------------------------------------

def dependency_parse(text: str) -> list[SentenceParse]:
    """Produce a :class:`SentenceParse` per sentence in *text*.

    Uses spaCy for dependency labels and POS tags.  The
    ``custom_parse_tree`` slot is left as ``None`` here — it is filled by
    the pipeline when the CYK parser is run.

    Parameters
    ----------
    text : str
        Multi-sentence text.

    Returns
    -------
    list[SentenceParse]
    """
    import time
    t0 = time.perf_counter()

    sentences = sent_tokenize(text)
    results: list[SentenceParse] = []
    for sent in sentences:
        token_analyses = _dependency_parse_spacy(sent)
        results.append(SentenceParse(tokens=token_analyses))

    elapsed = time.perf_counter() - t0
    logger.info("Stage 2 dep-parse: %d sentences in %.3fs",
                 len(results), elapsed)
    return results


def render_dep_tree_text(parse: SentenceParse) -> str:
    """Return a human-readable text rendering of a dependency parse."""
    lines: list[str] = []
    for tok in parse.tokens:
        dep_label = tok.dep
        head_label = tok.head if tok.head != tok.text else "(ROOT)"
        lines.append(f"  {tok.text:15s} [{tok.pos:6s}] <--{dep_label}-- {head_label}")
    return "\n".join(lines)


if __name__ == "__main__":
    test = "The cat sat on the mat. She opened the door."
    for sp in dependency_parse(test):
        print(render_dep_tree_text(sp))
        print()
