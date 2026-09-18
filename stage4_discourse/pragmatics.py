"""
Pragmatic inference — indirect-request detection via pattern matching.

Detects modal-interrogative openers (``could you …?``, ``would you …?``)
and emits a paraphrase of the implied action.
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
class PragmaticNote:
    """A pragmatic inference detected in a sentence."""
    surface_form: str       # the original sentence
    inferred_act: str       # "indirect_request"
    paraphrase: str         # implied action, e.g. "send me the file"


# ---------------------------------------------------------------------------
# Pattern list
# ---------------------------------------------------------------------------

_INDIRECT_PATTERNS: list[dict[str, Any]] = [
    {
        "pattern": re.compile(
            r"\b(could you|can you|would you|will you|would you mind)\b.+\?",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
    {
        "pattern": re.compile(
            r"\b(would it be possible|is it possible|do you think you could)\b.+\?",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
    {
        "pattern": re.compile(
            r"\b(i was wondering if|i wonder if|i wanted to ask)\b",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
    {
        "pattern": re.compile(
            r"\b(do you have|have you got|do you happen to have)\b.+\?",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
    {
        "pattern": re.compile(
            r"\b(i need|i would need|i would like|i'd like)\b",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
    {
        "pattern": re.compile(
            r"\b(if you could|if you would|when you get a chance|at your convenience)\b",
            re.IGNORECASE,
        ),
        "act": "indirect_request",
    },
]


def _extract_paraphrase(sentence: str) -> str:
    """Best-effort extraction of the implied action from an indirect request."""
    lower = sentence.lower()

    for verb_group in [
        r"\b(send|forward|share|email|give)\b\s+(.+?)(?:\?|$)",
        r"\b(look into|check|review|fix|update|escalate)\b\s*(.+?)(?:\?|$)",
        r"\b(help|assist)\b\s+(.+?)(?:\?|$)",
    ]:
        m = re.search(verb_group, lower)
        if m:
            return f"{m.group(1)}: {m.group(2).strip().rstrip('?').strip()}"

    return "implied action detected"


# ---------------------------------------------------------------------------
# Public API (spec-required signature)
# ---------------------------------------------------------------------------

def detect_indirect_request(sentence: str) -> PragmaticNote | None:
    """Detect whether *sentence* is an indirect request.

    Parameters
    ----------
    sentence : str
        A single sentence.

    Returns
    -------
    PragmaticNote or None
        ``None`` if the sentence is not an indirect request.
    """
    for rule in _INDIRECT_PATTERNS:
        if rule["pattern"].search(sentence):
            paraphrase = _extract_paraphrase(sentence)
            return PragmaticNote(
                surface_form=sentence,
                inferred_act=rule["act"],
                paraphrase=paraphrase,
            )
    return None


def detect_indirect_requests(text: str) -> list[PragmaticNote]:
    """Scan all sentences in *text* for indirect requests.

    Convenience wrapper that tokenises *text* into sentences and calls
    :func:`detect_indirect_request` on each.
    """
    import time
    t0 = time.perf_counter()

    sentences = sent_tokenize(text)
    results: list[PragmaticNote] = []
    for sent in sentences:
        note = detect_indirect_request(sent)
        if note is not None:
            results.append(note)

    elapsed = time.perf_counter() - t0
    logger.info("Pragmatic inference: %d indirect requests in %.3fs",
                 len(results), elapsed)
    return results


if __name__ == "__main__":
    tests = [
        "Could you send me the file?",
        "Would it be possible for you to reschedule the meeting?",
        "The weather is nice today.",
        "Can you help me with this assignment?",
    ]
    for s in tests:
        note = detect_indirect_request(s)
        if note:
            print(f"  [{note.inferred_act}] {note.surface_form}")
            print(f"    -> {note.paraphrase}")
        else:
            print(f"  [direct/statement] {s}")
