"""
Edit-distance computation — FROM SCRATCH.

This module implements the Levenshtein distance algorithm using the classic
dynamic-programming approach.  No external library (python-Levenshtein,
difflib.SequenceMatcher, etc.) is used for the distance calculation itself.

Implementation note: uses a two-row rolling array so memory is O(min(n, m))
instead of O(n·m).  The full O(n·m) table is never materialised.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def levenshtein_distance(s1: str, s2: str, limit: int | None = None) -> int:
    """Return the Levenshtein edit distance between *s1* and *s2*.

    Insert, delete, and substitute each cost 1.

    Parameters
    ----------
    s1, s2 : str
        The two strings to compare.
    limit : int or None
        Optional upper bound.  If the true distance exceeds *limit*, the
        function returns ``limit + 1`` early — useful when scanning a large
        dictionary and only candidates within a fixed radius are wanted.

    Returns
    -------
    int
        The edit distance (or ``limit + 1`` if it exceeds *limit*).
    """
    m, n = len(s1), len(s2)

    # Quick length-difference pruning
    if limit is not None and abs(m - n) > limit:
        return limit + 1

    # Two-row rolling array — O(min(n, m)) space
    prev: list[int] = list(range(n + 1))
    for i in range(1, m + 1):
        curr: list[int] = [i] + [0] * n
        ca = s1[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ca == s2[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,           # deletion
                curr[j - 1] + 1,       # insertion
                prev[j - 1] + cost,    # substitution
            )
        # Early termination: if every cell in this row already exceeds the
        # limit the final answer can never come back down.
        if limit is not None and min(curr) > limit:
            return limit + 1
        prev = curr

    return prev[n]
