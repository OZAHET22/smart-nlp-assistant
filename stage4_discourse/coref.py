"""
Coreference resolution — heuristic nearest-antecedent resolver with
gender/number agreement.

Attempts to use ``coreferee`` if available; falls back to the heuristic
resolver automatically.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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
class CorefChain:
    """A coreference chain linking mentions of the same entity."""
    mentions: list[str]     # surface forms in order, e.g. ["John", "he", "his"]
    entity_type: str        # "PERSON" | "OBJECT" | "UNKNOWN"


# ---------------------------------------------------------------------------
# Pronoun gender/number tables
# ---------------------------------------------------------------------------

MALE_PRONOUNS: set[str] = {"he", "him", "his", "himself"}
FEMALE_PRONOUNS: set[str] = {"she", "her", "hers", "herself"}
NEUTRAL_PRONOUNS: set[str] = {"it", "its", "itself"}
PLURAL_PRONOUNS: set[str] = {"they", "them", "their", "theirs", "themselves"}
ALL_PRONOUNS: set[str] = MALE_PRONOUNS | FEMALE_PRONOUNS | NEUTRAL_PRONOUNS | PLURAL_PRONOUNS

MALE_TITLES: set[str] = {
    "mr", "mr.", "dr", "dr.", "sir", "king", "prince", "father",
    "brother", "uncle", "son", "boy", "man", "husband",
}
FEMALE_TITLES: set[str] = {
    "mrs", "mrs.", "ms", "ms.", "miss", "queen", "princess",
    "mother", "sister", "aunt", "daughter", "girl", "woman", "wife",
}


def _get_pronoun_gender(pronoun: str) -> str:
    lower = pronoun.lower()
    if lower in MALE_PRONOUNS:
        return "male"
    if lower in FEMALE_PRONOUNS:
        return "female"
    if lower in PLURAL_PRONOUNS:
        return "plural"
    return "neutral"


def _get_noun_gender(token_text: str) -> str:
    lower = token_text.lower()
    if lower in MALE_TITLES:
        return "male"
    if lower in FEMALE_TITLES:
        return "female"
    return "unknown"


# ---------------------------------------------------------------------------
# spaCy singleton
# ---------------------------------------------------------------------------

def heuristic_coref_resolver(doc_or_text: Any) -> list[CorefChain]:
    """Resolve coreferences using nearest-antecedent heuristic with
    gender/number agreement.

    Works with either a spaCy Doc or plain text (NLTK fallback).
    """
    nlp = get_spacy()
    if nlp and not isinstance(doc_or_text, str):
        return _heuristic_from_spacy_doc(doc_or_text)
    if nlp and isinstance(doc_or_text, str):
        return _heuristic_from_spacy_doc(nlp(doc_or_text))
    return _heuristic_nltk(doc_or_text)


def _heuristic_from_spacy_doc(doc: Any) -> list[CorefChain]:
    """Heuristic coref over a spaCy Doc."""
    mentions: list[dict[str, Any]] = []
    pronoun_indices: list[int] = []

    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and token.dep_ != "compound":
            subtree = sorted(token.subtree, key=lambda t: t.i)
            mention_text = " ".join(t.text for t in subtree)
            gender = _get_noun_gender(token.text)
            is_plural = token.tag_ in ("NNS", "NNPS")
            etype = "PERSON" if token.ent_type_ == "PERSON" else "OBJECT"
            mentions.append({
                "text": mention_text, "idx": token.i,
                "gender": gender, "plural": is_plural,
                "type": "noun", "entity_type": etype,
            })
        elif token.text.lower() in ALL_PRONOUNS:
            pronoun_indices.append(len(mentions))
            mentions.append({
                "text": token.text, "idx": token.i,
                "gender": _get_pronoun_gender(token.text),
                "plural": token.text.lower() in PLURAL_PRONOUNS,
                "type": "pronoun", "entity_type": "UNKNOWN",
            })

    return _build_chains(mentions, pronoun_indices)


def _heuristic_nltk(text: str) -> list[CorefChain]:
    """Heuristic coref using NLTK (no dependency info)."""
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk import pos_tag

    sentences = sent_tokenize(text)
    mentions: list[dict[str, Any]] = []
    pronoun_indices: list[int] = []
    offset = 0

    for sent in sentences:
        tokens = word_tokenize(sent)
        tagged = pos_tag(tokens)
        for i, (word, tag) in enumerate(tagged):
            pos = offset + i
            if tag.startswith(("NN", "NNP")):
                mentions.append({
                    "text": word, "idx": pos,
                    "gender": _get_noun_gender(word),
                    "plural": tag in ("NNS", "NNPS"),
                    "type": "noun", "entity_type": "OBJECT",
                })
            elif word.lower() in ALL_PRONOUNS:
                pronoun_indices.append(len(mentions))
                mentions.append({
                    "text": word, "idx": pos,
                    "gender": _get_pronoun_gender(word),
                    "plural": word.lower() in PLURAL_PRONOUNS,
                    "type": "pronoun", "entity_type": "UNKNOWN",
                })
        offset += len(tokens)

    return _build_chains(mentions, pronoun_indices)


def _build_chains(
    mentions: list[dict[str, Any]],
    pronoun_indices: list[int],
) -> list[CorefChain]:
    """Match pronouns to nearest compatible antecedent and build chains."""
    chains: list[dict[str, Any]] = []

    for pidx in pronoun_indices:
        pron = mentions[pidx]
        p_gender = pron["gender"]
        p_plural = pron["plural"]

        best: dict[str, Any] | None = None
        best_dist = float("inf")

        for i, cand in enumerate(mentions):
            if i == pidx or cand["type"] == "pronoun":
                continue
            if cand["idx"] >= pron["idx"]:
                continue
            # Gender agreement
            if p_gender == "male" and cand["gender"] == "female":
                continue
            if p_gender == "female" and cand["gender"] == "male":
                continue
            # Number agreement
            if p_plural and not cand["plural"]:
                continue
            if not p_plural and cand["plural"]:
                continue

            dist = pron["idx"] - cand["idx"]
            if dist < best_dist:
                best_dist = dist
                best = cand

        if best is not None:
            # Try to add to existing chain
            added = False
            for chain in chains:
                if best["text"] in chain["mentions"]:
                    chain["mentions"].append(pron["text"])
                    added = True
                    break
            if not added:
                chains.append({
                    "main": best["text"],
                    "mentions": [best["text"], pron["text"]],
                    "entity_type": best["entity_type"],
                })

    return [
        CorefChain(mentions=c["mentions"], entity_type=c.get("entity_type", "UNKNOWN"))
        for c in chains
    ]


# ---------------------------------------------------------------------------
# Public API (spec-required signature)
# ---------------------------------------------------------------------------

def resolve_coreference(paragraph: str) -> list[CorefChain]:
    """Resolve pronoun coreferences across a paragraph.

    Attempts to use ``coreferee`` if installed; otherwise falls back to
    the heuristic nearest-antecedent resolver.

    Parameters
    ----------
    paragraph : str
        Multi-sentence text.

    Returns
    -------
    list[CorefChain]
    """
    import time
    t0 = time.perf_counter()

    # Try coreferee first
    try:
        import coreferee  # noqa: F401
        nlp = get_spacy()
        if nlp and hasattr(nlp, "add_pipe"):
            if "coreferee" not in nlp.pipe_names:
                nlp.add_pipe("coreferee")
            doc = nlp(paragraph)
            coref_data = getattr(doc._, "coref_chains", None)
            if coref_data:
                chains: list[CorefChain] = []
                for chain in coref_data:
                    # coreferee API: each chain is iterable of MentionSet;
                    # each MentionSet yields token indices.
                    try:
                        mention_texts = [
                            doc[mention[0]].text
                            for mention in chain
                        ]
                    except (TypeError, IndexError):
                        # Unexpected coreferee version — skip this chain
                        continue
                    if mention_texts:
                        chains.append(CorefChain(
                            mentions=mention_texts,
                            entity_type="UNKNOWN",
                        ))
                if chains:
                    logger.info(
                        "Coref (coreferee): %d chains in %.3fs",
                        len(chains), time.perf_counter() - t0
                    )
                    return chains
    except Exception:
        logger.debug("coreferee not available or failed, using heuristic fallback")

    # Heuristic fallback
    result = heuristic_coref_resolver(paragraph)
    logger.info("Coref (heuristic): %d chains in %.3fs",
                 len(result), time.perf_counter() - t0)
    return result


# Keep backward-compatible alias
resolve_coreferences = resolve_coreference


if __name__ == "__main__":
    import json
    test = ("John went to the store. He bought some milk. "
            "Sarah called her mother. She told her about the trip.")
    chains = resolve_coreference(test)
    for c in chains:
        print(f"  [{c.entity_type}] {' -> '.join(c.mentions)}")
