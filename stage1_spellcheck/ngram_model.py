"""
N-gram language model for context-aware spell-check disambiguation.

Trains bigram probabilities from the NLTK Brown corpus so that the spell
checker can resolve in-vocabulary confusables (there/their/they're, etc.)
by scoring each variant against its surrounding context.
"""

from __future__ import annotations

import os
import pickle
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


def build_from_brown(cache_path: str | None = None) -> NgramModel:
    """Build and return an NgramModel trained on the NLTK Brown corpus.

    Uses a cached pickle file if available to accelerate loading.
    """
    if cache_path is None:
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        cache_path = os.path.join(cache_dir, "brown_ngram_cache.pkl")

    if os.path.exists(cache_path):
        try:
            logger.info("Loading cached n-gram model from %s …", cache_path)
            with open(cache_path, "rb") as fh:
                model = pickle.load(fh)
            if isinstance(model, NgramModel) and len(model.vocab) > 0:
                return model
        except Exception as e:
            logger.warning("Could not load n-gram cache (%s), rebuilding: %s", cache_path, e)

    logger.info("Building n-gram model from Brown corpus …")
    model = NgramModel()
    model.train(brown.sents())

    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as fh:
            pickle.dump(model, fh, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info("Saved n-gram model cache to %s", cache_path)
    except Exception as e:
        logger.warning("Could not save n-gram cache to %s: %s", cache_path, e)

    return model
