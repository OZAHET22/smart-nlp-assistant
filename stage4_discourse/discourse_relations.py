"""
Discourse connective detection and relation labelling.

Detects connectives such as *however*, *because*, *moreover* and labels the
relation type (contrast / cause / cause_effect / elaboration) along with the
sentence indices being connected.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclass
# ---------------------------------------------------------------------------

@dataclass
class DiscourseRelation:
    """A discourse relation signalled by a connective."""
    connective: str
    relation: str           # "contrast" | "cause" | "cause_effect" | "elaboration"
    sentence_a: int         # index of the first sentence in the relation
    sentence_b: int         # index of the second sentence in the relation


# ---------------------------------------------------------------------------
# Connective lookup table
# ---------------------------------------------------------------------------

DISCOURSE_CONNECTIVES: dict[str, str] = {
    # contrast
    "however": "contrast", "but": "contrast", "although": "contrast",
    "yet": "contrast", "though": "contrast", "nevertheless": "contrast",
    "on the other hand": "contrast", "whereas": "contrast",
    "while": "contrast", "even though": "contrast", "nonetheless": "contrast",
    "in contrast": "contrast", "conversely": "contrast", "instead": "contrast",
    # cause_effect
    "therefore": "cause_effect", "thus": "cause_effect", "so": "cause_effect",
    "hence": "cause_effect", "consequently": "cause_effect",
    "as a result": "cause_effect", "accordingly": "cause_effect",
    # cause
    "because": "cause", "since": "cause", "due to": "cause",
    "owing to": "cause", "because of this": "cause",
    "for this reason": "cause",
    # elaboration
    "moreover": "elaboration", "furthermore": "elaboration",
    "in addition": "elaboration", "additionally": "elaboration",
    "also": "elaboration", "besides": "elaboration",
    "for example": "elaboration", "for instance": "elaboration",
    "in fact": "elaboration", "specifically": "elaboration",
    "what is more": "elaboration",
    # temporal
    "then": "temporal", "after": "temporal", "before": "temporal",
    "meanwhile": "temporal", "afterward": "temporal",
    "subsequently": "temporal", "previously": "temporal",
    "finally": "temporal", "eventually": "temporal",
    # condition
    "if": "condition", "unless": "condition",
    "provided that": "condition", "otherwise": "condition",
}

# Compile patterns (longest first to match multi-word connectives first)
_sorted_connectives = sorted(DISCOURSE_CONNECTIVES.keys(), key=len, reverse=True)
_CONNECTIVE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in _sorted_connectives) + r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Public API (spec-required signature)
# ---------------------------------------------------------------------------

def detect_discourse_relations(text: str) -> list[DiscourseRelation]:
    """Detect discourse connectives in *text* and label their relation type.

    For each connective found, ``sentence_a`` is the preceding sentence
    index (or 0 if the connective is in the first sentence) and
    ``sentence_b`` is the sentence that contains the connective.

    Parameters
    ----------
    text : str
        Multi-sentence paragraph.

    Returns
    -------
    list[DiscourseRelation]
    """
    import time
    t0 = time.perf_counter()

    sentences = sent_tokenize(text)
    relations: list[DiscourseRelation] = []

    for sent_idx, sentence in enumerate(sentences):
        for match in _CONNECTIVE_PATTERN.finditer(sentence):
            connective = match.group(0).lower()
            relation = DISCOURSE_CONNECTIVES.get(connective)
            if relation is None:
                continue
            # The connective connects the current sentence to the previous one
            sentence_a = max(0, sent_idx - 1)
            sentence_b = sent_idx
            relations.append(DiscourseRelation(
                connective=connective,
                relation=relation,
                sentence_a=sentence_a,
                sentence_b=sentence_b,
            ))

    elapsed = time.perf_counter() - t0
    logger.info("Discourse relations: %d found in %.3fs",
                 len(relations), elapsed)
    return relations


if __name__ == "__main__":
    test = ("The weather was terrible. However, we decided to go hiking. "
            "Because the trail was muddy, we had to be careful. "
            "Eventually we reached the summit.")
    for r in detect_discourse_relations(test):
        print(f"  [{r.relation:12s}] '{r.connective}' "
              f"  (sentence {r.sentence_a} -> {r.sentence_b})")
