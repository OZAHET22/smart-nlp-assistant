"""
Context-free grammar definition for the hand-built parser.

Provides a 15-rule CFG covering simple declarative sentences, wrapped in the
spec-required :class:`CFGGrammar` class.
"""

from __future__ import annotations


class CFGGrammar:
    """Container for a context-free grammar specified as a dict of rules.

    Parameters
    ----------
    rules : dict[str, list[list[str]]]
        Mapping from non-terminal symbol to a list of productions, where
        each production is a list of symbols (terminals or non-terminals).
    """

    def __init__(self, rules: dict[str, list[list[str]]]) -> None:
        self.rules = rules

    def nonterminals(self) -> list[str]:
        """Return all non-terminal symbols."""
        return list(self.rules.keys())

    def productions(self, symbol: str) -> list[list[str]]:
        """Return the list of productions for *symbol*."""
        return self.rules.get(symbol, [])


# 15-rule grammar for simple declarative sentences
GRAMMAR_RULES: dict[str, list[list[str]]] = {
    "S":    [["NP", "VP"]],
    "NP":   [["DT", "NN"], ["DT", "JJ", "NN"], ["PRP"], ["NNP"],
             ["DT", "NN", "PP"], ["DT", "JJ", "NN", "PP"]],
    "VP":   [["VB", "NP"], ["VBD", "NP"], ["VBZ", "NP"],
             ["VB", "PP"], ["VBD", "PP"], ["VBZ", "PP"],
             ["VB", "NP", "PP"], ["VBD", "NP", "PP"], ["VBZ", "NP", "PP"],
             ["VB"], ["VBD"], ["VBZ"],
             ["MD", "VP"]],
    "PP":   [["IN", "NP"]],
}

POS_MAP: dict[str, list[str] | None] = {
    "DT":   ["the", "a", "an", "this", "that", "these", "those", "my", "his",
             "her", "its", "our", "their", "your", "some", "any", "no", "every"],
    "NN":   None,
    "NNP":  None,
    "JJ":   None,
    "PRP":  ["i", "you", "he", "she", "it", "we", "they", "me", "him",
             "her", "us", "them"],
    "VB":   None,
    "VBD":  None,
    "VBZ":  None,
    "IN":   ["in", "on", "at", "to", "for", "with", "by", "from", "of",
             "about", "into", "through", "during", "before", "after",
             "above", "below", "between", "under", "over", "near"],
    "MD":   ["can", "could", "will", "would", "shall", "should", "may",
             "might", "must"],
}


# Pre-built CFGGrammar instance
DEFAULT_GRAMMAR = CFGGrammar(GRAMMAR_RULES)
