"""
Named Entity Recognition — spaCy backed with NLTK fallback.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

try:
    from utils import get_spacy
except ImportError:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from utils import get_spacy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclass
# ---------------------------------------------------------------------------

@dataclass
class Entity:
    """A named entity span."""
    text: str
    label: str
    start: int
    end: int


# ---------------------------------------------------------------------------
# spaCy singleton
# ---------------------------------------------------------------------------

def extract_entities(text: str) -> list[Entity]:
    """Extract named entities from *text*.

    Uses spaCy ``doc.ents``.  Falls back to NLTK ``ne_chunk`` if spaCy is
    unavailable.
    """
    nlp = get_spacy()
    if nlp:
        doc = nlp(text)
        return [
            Entity(text=ent.text, label=ent.label_,
                   start=ent.start_char, end=ent.end_char)
            for ent in doc.ents
        ]
    return _extract_entities_nltk(text)


def _extract_entities_nltk(text: str) -> list[Entity]:
    """Fallback NER via NLTK chunker."""
    from nltk import pos_tag, ne_chunk
    from nltk.tokenize import word_tokenize

    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    tree = ne_chunk(tagged)

    entities: list[Entity] = []
    for subtree in tree:
        if hasattr(subtree, "label"):
            entity_text = " ".join(w for w, _ in subtree.leaves())
            entities.append(Entity(text=entity_text, label=subtree.label(),
                                   start=-1, end=-1))
    return entities


if __name__ == "__main__":
    test = "John went to New York last Friday to meet Dr. Smith at the United Nations."
    for e in extract_entities(test):
        print(f"  {e.text:25s} [{e.label}]  ({e.start}:{e.end})")
