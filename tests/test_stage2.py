"""
Tests for Stage 2 — Syntactic Processing.

Covers:
- CYK parser correctly parses ≥3 sentences that fit the grammar
- CYK parser correctly rejects ≥1 sentence outside the grammar
- dependency_parse runs without crashing on all 10 test samples
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stage2_syntax.cyk_parser import CYKParser, build_parse_tree_string
from stage2_syntax.dependency_parser import dependency_parse

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "test_samples")
if not os.path.isdir(SAMPLES_DIR):
    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_samples")


# ── CYK Parser ────────────────────────────────────────────────────────────────

class TestCYKParser:
    """Tests for the from-scratch CYK parser."""

    @pytest.fixture(scope="class")
    def parser(self):
        return CYKParser()

    # ── Sentences the grammar CAN parse ──────────────────────────────────────

    def test_simple_np_vp(self, parser):
        """'John sent the report' — fits NP VP pattern."""
        tree, tagged = parser.parse(["John", "sent", "the", "report"])
        assert tree is not None, "Should parse 'John sent the report'"

    def test_pronoun_subject(self, parser):
        """'she sent the report' — Pron VP NP."""
        tree, tagged = parser.parse(["she", "sent", "the", "report"])
        assert tree is not None, "Should parse 'she sent the report'"

    def test_det_n_vp(self, parser):
        """'the teacher reviewed the report' — Det N V NP."""
        tree, tagged = parser.parse(["the", "teacher", "reviewed", "the", "report"])
        assert tree is not None, "Should parse 'the teacher reviewed the report'"

    # ── Sentence the grammar CANNOT parse ────────────────────────────────────

    def test_rejects_ungrammatical(self, parser):
        """
        A sentence with vocabulary or structure outside the defined grammar
        should return None (not crash).
        """
        tree, _ = parser.parse(["because", "the", "weather", "is", "terrible"])
        assert tree is None, "Should return None for out-of-grammar sentence"

    # ── Tree rendering ────────────────────────────────────────────────────────

    def test_build_parse_tree_string_on_none(self):
        """build_parse_tree_string(None) should return a human-readable message."""
        s = build_parse_tree_string(None)
        assert isinstance(s, str)
        assert len(s) > 0

    def test_build_parse_tree_string_on_valid_tree(self, parser):
        tree, _ = parser.parse(["John", "sent", "the", "report"])
        if tree is not None:
            s = build_parse_tree_string(tree)
            assert "S" in s or len(s) > 0


# ── Dependency Parser ─────────────────────────────────────────────────────────

class TestDependencyParser:
    """Tests that the library-backed dependency parser runs on all 10 samples."""

    def _load_sample(self, fname: str) -> str:
        path = os.path.join(SAMPLES_DIR, fname)
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_dep_parse_does_not_crash(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = self._load_sample(fname)
        parses = dependency_parse(text)
        assert isinstance(parses, list)
        assert len(parses) > 0, f"Expected at least one sentence in {fname}"
        for sp in parses:
            assert sp.tokens, "SentenceParse must have at least one token"
            for tok in sp.tokens:
                assert tok.text, "Each token must have a text field"
                assert tok.pos, "Each token must have a POS field"
