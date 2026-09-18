"""
POS tagger — thin wrapper around spaCy (with NLTK fallback).
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from utils import get_spacy
except ImportError:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from utils import get_spacy

logger = logging.getLogger(__name__)


def pos_tag_sentence(sentence: str) -> list[tuple[str, str]]:
    """Return a list of ``(word, POS-tag)`` pairs for *sentence*."""
    nlp = get_spacy()
    if nlp:
        doc = nlp(sentence)
        return [(tok.text, tok.tag_) for tok in doc]
    else:
        from nltk import pos_tag
        from nltk.tokenize import word_tokenize
        return pos_tag(word_tokenize(sentence))


def pos_tag_bulk(sentences: list[str]) -> list[list[tuple[str, str]]]:
    """POS-tag multiple sentences."""
    return [pos_tag_sentence(s) for s in sentences]
