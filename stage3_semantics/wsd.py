"""
Word Sense Disambiguation using the simplified Lesk algorithm.

Disambiguates target ambiguous words (bank, bat, light, etc.) by comparing
WordNet gloss overlap with the sentence context.
"""

from __future__ import annotations

import logging
from typing import Any

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

TARGET_WORDS: set[str] = {
    "bank", "bat", "light", "plant", "spring", "crane", "match", "ring",
}


def lesk_wsd(word: str, context_tokens: list[str]) -> tuple[Any, int]:
    """Lesk-style WSD: return ``(best_synset, overlap_score)`` for *word*.

    Parameters
    ----------
    word : str
        The ambiguous word.
    context_tokens : list[str]
        The surrounding sentence tokens (lowercased).

    Returns
    -------
    tuple[nltk.corpus.wordnet.Synset | None, int]
        Best synset (or ``None`` if no synsets exist) and the integer
        overlap score used to select it.
    """
    context_set = set(context_tokens) - {word.lower()}
    synsets = wn.synsets(word)
    if not synsets:
        return None, 0

    best_synset = None
    best_overlap = -1

    for syn in synsets:
        gloss_words = set(word_tokenize(
            (syn.definition() + " " + " ".join(syn.examples())).lower()
        ))
        overlap = len(context_set & gloss_words)

        # Extend with hypernym glosses for richer overlap
        for hyper in syn.hypernyms():
            hyper_gloss = set(word_tokenize(hyper.definition().lower()))
            overlap += len(context_set & hyper_gloss)

        if overlap > best_overlap:
            best_overlap = overlap
            best_synset = syn

    if best_synset is None:
        return synsets[0], 0
    return best_synset, best_overlap


def simplified_lesk(word: str, sentence: str) -> dict[str, Any] | None:
    """Return a dict with the best sense, definition, and overlap score.

    Convenience wrapper around :func:`lesk_wsd` that adds metadata useful
    for display and testing.
    """
    tokens = word_tokenize(sentence.lower())
    synset, overlap = lesk_wsd(word, tokens)
    if synset is None:
        return None
    return {
        "word": word,
        "sense": synset.name(),
        "definition": synset.definition(),
        "overlap_score": overlap,   # real overlap count, not -1
        "pos": synset.pos(),
    }


def disambiguate(
    text: str,
    target_words: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Run WSD on all target words found in *text*.

    Returns a list of dicts, each with keys ``word``, ``sense``,
    ``definition``.
    """
    if target_words is None:
        target_words = TARGET_WORDS

    tokens = word_tokenize(text.lower())
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    for token in tokens:
        if token in target_words and token not in seen:
            result = simplified_lesk(token, text)
            if result:
                results.append(result)
                seen.add(token)

    return results


if __name__ == "__main__":
    test_cases = [
        "I went to the bank to deposit my money.",
        "The bat flew out of the cave at night.",
        "He hit the ball with a bat.",
        "The river bank was flooded after the storm.",
    ]
    for sent in test_cases:
        print(f"\nSentence: {sent}")
        for r in disambiguate(sent):
            print(f"  {r['word']:10s} -> {r['sense']:30s} | {r['definition']}")
