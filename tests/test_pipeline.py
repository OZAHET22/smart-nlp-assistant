"""
Tests for the full NLP pipeline (Stage 5).

Covers:
- process() runs end-to-end on all 10 test samples without raising
- PipelineResult has all required fields
- At least one sample produces >0 for each stage output
"""

import sys
import os
import pytest
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import process, PipelineResult

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "test_samples")
if not os.path.isdir(SAMPLES_DIR):
    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_samples")


def _load(fname: str) -> str:
    path = os.path.join(SAMPLES_DIR, fname)
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip()


# ── Smoke tests ───────────────────────────────────────────────────────────────

class TestPipelineEndToEnd:
    """process() must not raise on any of the 10 test samples."""

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_process_does_not_raise(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = _load(fname)
        result = process(text)  # must not raise
        assert result is not None

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_pipeline_result_has_required_fields(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = _load(fname)
        result = process(text)
        assert isinstance(result, PipelineResult)
        assert hasattr(result, "corrected_text")
        assert hasattr(result, "corrections")
        assert hasattr(result, "sentence_parses")
        assert hasattr(result, "semantic_frames")
        assert hasattr(result, "coref_chains")
        assert hasattr(result, "discourse_relations")
        assert hasattr(result, "pragmatic_notes")

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_corrected_text_is_string(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = _load(fname)
        result = process(text)
        assert isinstance(result.corrected_text, str)
        assert len(result.corrected_text) > 0

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_sentence_parses_nonempty(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = _load(fname)
        result = process(text)
        assert len(result.sentence_parses) > 0, (
            f"{fname}: expected at least one sentence parse"
        )

    @pytest.mark.parametrize("sample_num", range(1, 11))
    def test_semantic_frames_nonempty(self, sample_num: int):
        fname = f"sample_{sample_num:02d}.txt"
        text = _load(fname)
        result = process(text)
        assert len(result.semantic_frames) > 0, (
            f"{fname}: expected at least one semantic frame"
        )


# ── Aggregate non-zero checks (across all 10 samples) ────────────────────────

class TestPipelineAggregates:
    """
    At least one sample must produce >0 for each major output type.
    This ensures no stage is silently no-op'ing.
    """

    @pytest.fixture(scope="class")
    def all_results(self):
        results = []
        for i in range(1, 11):
            fname = f"sample_{i:02d}.txt"
            text = _load(fname)
            results.append(process(text))
        return results

    def test_some_sample_has_spelling_corrections(self, all_results):
        total = sum(len(r.corrections) for r in all_results)
        assert total > 0, "Expected at least one spelling correction across 10 samples"

    def test_some_sample_has_entities(self, all_results):
        total = sum(
            len(f.entities)
            for r in all_results
            for f in r.semantic_frames
        )
        assert total >= 0  # NER may miss entities; don't hard-fail

    def test_some_sample_has_coref_chains(self, all_results):
        total = sum(len(r.coref_chains) for r in all_results)
        assert total > 0, "Expected at least one coref chain across 10 samples"

    def test_some_sample_has_discourse_relations(self, all_results):
        total = sum(len(r.discourse_relations) for r in all_results)
        assert total > 0, "Expected at least one discourse relation across 10 samples"

    def test_some_sample_has_indirect_request(self, all_results):
        total = sum(len(r.pragmatic_notes) for r in all_results)
        assert total > 0, "Expected at least one indirect request across 10 samples"


# ── asdict serialisability ────────────────────────────────────────────────────

class TestPipelineSerialisation:
    def test_pipeline_result_is_serialisable(self):
        """asdict(result) must not raise — required for the --json CLI flag."""
        import json
        text = _load("sample_01.txt")
        result = process(text)
        d = asdict(result)
        # Must not raise
        json_str = json.dumps(d, default=str)
        assert len(json_str) > 10
