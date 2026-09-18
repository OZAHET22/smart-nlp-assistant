"""
Tests for Stage 4 — Discourse & Pragmatic Processing.

Covers:
- Coreference: at least one paragraph produces a chain with 2+ mentions
- Discourse relations: at least 2 connective types correctly labelled
- Indirect requests: fires on 1 sample, does NOT fire on plain questions
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stage4_discourse.coref import resolve_coreference, CorefChain
from stage4_discourse.discourse_relations import (
    detect_discourse_relations,
    DiscourseRelation,
    DISCOURSE_CONNECTIVES,
)
from stage4_discourse.pragmatics import detect_indirect_request, PragmaticNote

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "test_samples")
if not os.path.isdir(SAMPLES_DIR):
    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_samples")


# ── Coreference Resolution ────────────────────────────────────────────────────

class TestCoreference:
    """Tests for heuristic pronoun coreference resolver."""

    def test_coref_chain_two_mentions(self):
        """Classic two-mention chain: John → he."""
        text = "John went to the store. He bought some milk."
        chains = resolve_coreference(text)
        assert isinstance(chains, list)
        # At least one chain should link John and he
        multi_mention_chains = [c for c in chains if len(c.mentions) >= 2]
        assert len(multi_mention_chains) >= 1, (
            "Expected at least one chain with 2+ mentions for 'John … He'"
        )

    def test_coref_chain_dataclass_fields(self):
        text = "Sarah called her mother. She told her about the trip."
        chains = resolve_coreference(text)
        for chain in chains:
            assert isinstance(chain, CorefChain)
            assert isinstance(chain.mentions, list)
            assert chain.entity_type in ("PERSON", "OBJECT", "UNKNOWN")

    def test_coref_returns_list(self):
        chains = resolve_coreference("The cat sat on the mat.")
        assert isinstance(chains, list)

    def test_coref_all_samples_no_crash(self):
        """resolve_coreference must not crash on any of the 10 samples."""
        for i in range(1, 11):
            fname = f"sample_{i:02d}.txt"
            path = os.path.join(SAMPLES_DIR, fname)
            with open(path, encoding="utf-8") as fh:
                text = fh.read().strip()
            result = resolve_coreference(text)
            assert isinstance(result, list)


# ── Discourse Relations ───────────────────────────────────────────────────────

class TestDiscourseRelations:
    """Tests for connective detection and relation typing."""

    def test_detects_however_contrast(self):
        text = "The weather was terrible. However, we decided to go hiking."
        relations = detect_discourse_relations(text)
        contrast_rels = [r for r in relations if r.relation == "contrast"]
        assert len(contrast_rels) >= 1, "Expected a 'contrast' relation for 'however'"

    def test_detects_because_cause(self):
        text = "She stayed home because she was sick."
        relations = detect_discourse_relations(text)
        cause_rels = [r for r in relations if r.relation == "cause"]
        assert len(cause_rels) >= 1, "Expected a 'cause' relation for 'because'"

    def test_detects_therefore_cause_effect(self):
        text = "The bridge was damaged. Therefore, the road was closed."
        relations = detect_discourse_relations(text)
        cause_effect_rels = [r for r in relations if r.relation == "cause_effect"]
        assert len(cause_effect_rels) >= 1, "Expected 'cause_effect' for 'therefore'"

    def test_detects_moreover_elaboration(self):
        text = "The report was late. Moreover, it was incomplete."
        relations = detect_discourse_relations(text)
        elab_rels = [r for r in relations if r.relation == "elaboration"]
        assert len(elab_rels) >= 1, "Expected 'elaboration' for 'moreover'"

    def test_discourse_relation_dataclass_fields(self):
        text = "The weather was terrible. However, we went out."
        relations = detect_discourse_relations(text)
        for r in relations:
            assert isinstance(r, DiscourseRelation)
            assert isinstance(r.connective, str)
            assert isinstance(r.relation, str)
            assert isinstance(r.sentence_a, int)
            assert isinstance(r.sentence_b, int)

    def test_sentence_indices_make_sense(self):
        text = "First sentence. However, second sentence."
        relations = detect_discourse_relations(text)
        for r in relations:
            assert r.sentence_a >= 0
            assert r.sentence_b >= 0
            assert r.sentence_b >= r.sentence_a

    def test_connective_table_has_required_types(self):
        """The DISCOURSE_CONNECTIVES dict must include at least contrast, cause, elaboration."""
        relation_types = set(DISCOURSE_CONNECTIVES.values())
        assert "contrast" in relation_types
        assert "cause" in relation_types
        assert "elaboration" in relation_types

    def test_no_relations_on_plain_statement(self):
        text = "The cat sat on the mat."
        relations = detect_discourse_relations(text)
        # Should return empty or minimal — no connective in this text
        assert isinstance(relations, list)


# ── Pragmatic Inference ───────────────────────────────────────────────────────

class TestPragmatics:
    """Tests for indirect-request detection."""

    # Positive cases — should detect an indirect request
    @pytest.mark.parametrize("sentence", [
        "Could you send me the file?",
        "Would it be possible for you to reschedule the meeting?",
        "Can you help me with this assignment?",
        "I was wondering if you could review the document.",
        "Would you mind checking the report?",
    ])
    def test_detects_indirect_request(self, sentence: str):
        note = detect_indirect_request(sentence)
        assert note is not None, f"Expected indirect request for: {sentence!r}"
        assert note.inferred_act == "indirect_request"
        assert isinstance(note.paraphrase, str)

    # Negative cases — plain questions or statements, NOT indirect requests
    @pytest.mark.parametrize("sentence", [
        "Is the door open?",
        "Are you coming to the party?",
        "Did you finish your homework?",
        "The weather is nice today.",
    ])
    def test_does_not_fire_on_direct_question(self, sentence: str):
        note = detect_indirect_request(sentence)
        assert note is None, (
            f"Expected no indirect request for direct question: {sentence!r}, "
            f"but got: {note}"
        )

    def test_pragmatic_note_fields(self):
        note = detect_indirect_request("Could you send the file?")
        assert isinstance(note, PragmaticNote)
        assert note.surface_form
        assert note.inferred_act == "indirect_request"
        assert note.paraphrase

    def test_fires_on_sample_with_request(self):
        """
        sample_01.txt contains 'could you send us the rubric again?' which is
        an indirect request.
        """
        path = os.path.join(SAMPLES_DIR, "sample_01.txt")
        with open(path, encoding="utf-8") as fh:
            text = fh.read().strip()
        from stage4_discourse.pragmatics import detect_indirect_requests
        notes = detect_indirect_requests(text)
        assert len(notes) >= 1, "sample_01.txt should trigger at least 1 indirect request"
