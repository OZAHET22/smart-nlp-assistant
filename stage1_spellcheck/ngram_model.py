"""
N-gram language model for context-aware spell-check disambiguation.

Trains bigram probabilities from the NLTK Brown corpus so that the spell
checker can resolve in-vocabulary confusables (there/their/they're, etc.)
by scoring each variant against its surrounding context.
"""

from __future__ import annotations

import logging
from collections import Counter

from nltk.corpus import brown

logger = logging.getLogger(__name__)


class NgramModel:
    """Simple bigram language model with add-one smoothing."""

    def __init__(self) -> None:
        self.unigrams: Counter[str] = Counter()
        self.bigrams: Counter[tuple[str, str]] = Counter()
        self.total: int = 0
        self.vocab: set[str] = set()

    def train(self, sentences: list[list[str]]) -> None:
        """Train on a list of tokenised sentences."""
        for sent in sentences:
            tokens = [t.lower() for t in sent if t.isalpha()]
            self.unigrams.update(tokens)
            for a, b in zip(tokens, tokens[1:]):
                self.bigrams[(a, b)] += 1
            self.total += len(tokens)
        self.vocab = set(self.unigrams.keys())
        logger.info("NgramModel trained: %d unigrams, %d bigram types",
                     len(self.vocab), len(self.bigrams))

    def known(self, word: str) -> bool:
        """Return True if *word* is in the training vocabulary."""
        return word in self.vocab

    def p_given(self, prev: str, word: str) -> float:
        """P(word | prev) with add-one smoothing."""
        denominator = self.unigrams[prev] + len(self.vocab) + 1
        return (self.bigrams.get((prev, word), 0) + 1) / denominator

    def score_in_context(self, word: str, prev: str, nxt: str = "") -> float:
        """Score *word* using bigram probabilities with its neighbours.

        Combines ``P(word | prev)`` and ``P(nxt | word)`` to give a rough
        measure of how well *word* fits between *prev* and *nxt*.
        """
        p: float = (
            self.p_given(prev, word) if prev
            else self.unigrams[word] / max(self.total, 1)
        )
        if nxt:
            p *= self.p_given(word, nxt)
        return p


def build_from_brown() -> NgramModel:
    """Build and return an NgramModel trained on the NLTK Brown corpus."""
    logger.info("Building n-gram model from Brown corpus …")
    model = NgramModel()
    model.train(brown.sents())
    return model
