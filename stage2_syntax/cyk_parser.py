"""
CYK (Cocke–Younger–Kasami) parser — FROM SCRATCH.

This module implements a CYK parser that converts the grammar to Chomsky
Normal Form internally.  No external parsing library is used for the actual
parsing algorithm.  POS tagging is delegated to spaCy (or NLTK as fallback)
because tag assignment is not the from-scratch requirement — the *parser* is.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from nltk.tokenize import word_tokenize

try:
    from .grammar import GRAMMAR_RULES, CFGGrammar
except ImportError:
    from grammar import GRAMMAR_RULES, CFGGrammar

try:
    from utils import get_spacy
except ImportError:
    try:
        from ..utils import get_spacy
    except ImportError:
        import sys, os as _os
        sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
        from utils import get_spacy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parse-tree type (simple nested tuples)
# ---------------------------------------------------------------------------

ParseTree = tuple[Any, ...]   # recursive: (label, child1, child2, …)

# ---------------------------------------------------------------------------
# POS tagger (thin wrapper — NOT the from-scratch part)
# ---------------------------------------------------------------------------

def _pos_tag(tokens: list[str]) -> list[tuple[str, str]]:
    """Tag *tokens* using spaCy (preferred) or NLTK."""
    nlp = get_spacy()
    if nlp:
        doc = nlp(" ".join(tokens))
        return [(tok.text, tok.tag_) for tok in doc]
    else:
        from nltk import pos_tag
        return pos_tag(tokens)


# ---------------------------------------------------------------------------
# CYK Parser
# ---------------------------------------------------------------------------

class CYKParser:
    """CYK chart parser with automatic CNF conversion.

    Parameters
    ----------
    grammar : dict or CFGGrammar, optional
        Grammar rules.  Defaults to ``GRAMMAR_RULES``.
    """

    def __init__(self, grammar: dict[str, list[list[str]]] | CFGGrammar | None = None) -> None:
        if isinstance(grammar, CFGGrammar):
            self.grammar = grammar.rules
        else:
            self.grammar = grammar if grammar else GRAMMAR_RULES
        self._cnf_grammar: dict[tuple[str, str], list[str]] = {}
        self._unit_rules: dict[str, list[str]] = {}
        self._convert_to_cnf()

    def _convert_to_cnf(self) -> None:
        """Convert the stored grammar to Chomsky Normal Form."""
        self._cnf_grammar = {}
        self._unit_rules = {}
        counter = 0

        for lhs, productions in self.grammar.items():
            for prod in productions:
                if len(prod) == 1:
                    self._unit_rules.setdefault(prod[0], []).append(lhs)
                elif len(prod) == 2:
                    self._cnf_grammar.setdefault(
                        (prod[0], prod[1]), []).append(lhs)
                else:
                    symbols = list(prod)
                    while len(symbols) > 2:
                        right = symbols.pop()
                        left = symbols.pop()
                        new_nt = f"_X{counter}"
                        counter += 1
                        self._cnf_grammar.setdefault(
                            (left, right), []).append(new_nt)
                        symbols.append(new_nt)
                    self._cnf_grammar.setdefault(
                        (symbols[0], symbols[1]), []).append(lhs)

    def parse(self, sentence: str | list[str]) -> tuple[ParseTree | None, list[tuple[str, str]]]:
        """Parse *sentence* and return ``(tree, tagged_tokens)``.

        Parameters
        ----------
        sentence : str or list[str]
            A sentence string or pre-tokenised list.

        Returns
        -------
        tuple[ParseTree | None, list[tuple[str, str]]]
            The parse tree (or ``None`` if the sentence is outside the
            grammar) and the POS-tagged token list.
        """
        if isinstance(sentence, str):
            tokens = word_tokenize(sentence)
        else:
            tokens = list(sentence)

        tagged = _pos_tag(tokens)
        tokens = [w for w, _ in tagged]
        tags = [t for _, t in tagged]
        n = len(tags)

        if n == 0:
            return None, tagged

        # CYK table
        table: list[list[set[str]]] = [[set() for _ in range(n)] for _ in range(n)]
        back: list[list[dict[str, tuple[Any, ...]]]] = [
            [{} for _ in range(n)] for _ in range(n)
        ]

        # Fill diagonal (single tokens)
        for i in range(n):
            tag = tags[i]
            table[i][i].add(tag)
            back[i][i][tag] = ("terminal", tokens[i])

            if tag in self._unit_rules:
                for parent in self._unit_rules[tag]:
                    table[i][i].add(parent)
                    back[i][i][parent] = ("unit", tag)

        # Fill rest of the chart
        for span in range(2, n + 1):
            for i in range(n - span + 1):
                j = i + span - 1
                for k in range(i, j):
                    for b_sym in table[i][k]:
                        for c_sym in table[k + 1][j]:
                            pair = (b_sym, c_sym)
                            if pair in self._cnf_grammar:
                                for a_sym in self._cnf_grammar[pair]:
                                    if a_sym not in table[i][j]:
                                        table[i][j].add(a_sym)
                                        back[i][j][a_sym] = ("split", k, b_sym, c_sym)

                # Propagate unit rules
                changed = True
                while changed:
                    changed = False
                    additions: dict[str, tuple[Any, ...]] = {}
                    for sym in table[i][j]:
                        if sym in self._unit_rules:
                            for parent in self._unit_rules[sym]:
                                if parent not in table[i][j]:
                                    additions[parent] = ("unit", sym)
                                    changed = True
                    for parent, info in additions.items():
                        table[i][j].add(parent)
                        back[i][j].setdefault(parent, info)

        if "S" in table[0][n - 1]:
            tree = self._build_tree(back, 0, n - 1, "S")
            return tree, tagged
        return None, tagged

    def _build_tree(
        self,
        back: list[list[dict[str, tuple[Any, ...]]]],
        i: int, j: int, symbol: str,
    ) -> ParseTree:
        """Recursively reconstruct the parse tree from the back-pointer table."""
        entry = back[i][j].get(symbol)
        if entry is None:
            return (symbol,)

        if entry[0] == "terminal":
            return (symbol, entry[1])
        elif entry[0] == "unit":
            child_tree = self._build_tree(back, i, j, entry[1])
            return (symbol, child_tree)
        elif entry[0] == "split":
            k, b_sym, c_sym = entry[1], entry[2], entry[3]
            left = self._build_tree(back, i, k, b_sym)
            right = self._build_tree(back, k + 1, j, c_sym)
            return (symbol, left, right)
        return (symbol,)


# ---------------------------------------------------------------------------
# Tree rendering
# ---------------------------------------------------------------------------

def build_parse_tree_string(tree: ParseTree | None, indent: int = 0) -> str:
    """Return a human-readable indented string representation of *tree*."""
    if tree is None:
        return "  (no parse found for this sentence with the given grammar)"

    prefix = "  " * indent
    if isinstance(tree, str):
        return prefix + tree

    if len(tree) == 1:
        return prefix + f"({tree[0]})"

    if len(tree) == 2 and isinstance(tree[1], str):
        return prefix + f"({tree[0]} {tree[1]})"

    lines = [prefix + f"({tree[0]}"]
    for child in tree[1:]:
        lines.append(build_parse_tree_string(child, indent + 1))
    lines.append(prefix + ")")
    return "\n".join(lines)


def render_tree(tree: ParseTree | None, out_path: str) -> None:
    """Render *tree* to a text file at *out_path*.

    Creates parent directories if necessary.

    Parameters
    ----------
    tree : ParseTree or None
        The parse tree to render.
    out_path : str
        File path to write the tree representation to.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    text = build_parse_tree_string(tree)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    logger.info("Parse tree written to %s", out_path)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = CYKParser()
    test_sentences = [
        "the cat sat on the mat",
        "he can read the book",
        "she opened the door",
    ]
    for sent in test_sentences:
        print(f"\nSentence: {sent}")
        tree, tagged = parser.parse(sent)
        print(f"POS tags: {tagged}")
        print("Parse tree:")
        print(build_parse_tree_string(tree))
        print("-" * 50)
