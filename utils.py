"""
Shared utilities for the NLP pipeline.

Provides a single spaCy model singleton so all pipeline stages share the
same ``en_core_web_sm`` instance instead of each loading their own copy
(which wastes ~50 MB per duplicate load).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_spacy_nlp: Any = None


def get_spacy() -> Any:
    """Return the shared spaCy ``en_core_web_sm`` model.

    Loads the model on the first call and caches it for the lifetime of
    the process.  Returns ``False`` (not ``None``) when spaCy or the model
    is unavailable, so callers can branch on a simple truthy check::

        nlp = get_spacy()
        if nlp:
            doc = nlp(text)
        else:
            # NLTK fallback path
            ...

    Returns
    -------
    spacy.Language or False
        The loaded spaCy model, or ``False`` if unavailable.
    """
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy  # noqa: PLC0415
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model 'en_core_web_sm' loaded (shared singleton).")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "spaCy model unavailable (%s). NLTK fallback will be used.", exc
            )
            _spacy_nlp = False
    return _spacy_nlp
