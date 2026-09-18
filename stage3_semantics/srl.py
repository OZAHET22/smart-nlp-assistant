"""
Semantic Role Labelling (rule-based over the dependency tree) and unified
semantic analysis combining NER + SRL + WSD.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from nltk.tokenize import sent_tokenize, word_tokenize

try:
    from .ner import Entity, extract_entities
    from .wsd import disambiguate, lesk_wsd, TARGET_WORDS
except ImportError:
    from ner import Entity, extract_entities
    from wsd import disambiguate, lesk_wsd, TARGET_WORDS

try:
    from utils import get_spacy
except ImportError:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from utils import get_spacy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclass
# ---------------------------------------------------------------------------

@dataclass
class SemanticFrame:
    """Semantic role frame for a single sentence."""
    sentence: str
    agent: str | None
    action: str | None
    patient: str | None
    entities: list[Entity]
    word_senses: dict[str, str]   # e.g. {"bank": "bank.n.01"}


# ---------------------------------------------------------------------------
# spaCy singleton
# ---------------------------------------------------------------------------

AGENT_DEPS: set[str] = {"nsubj", "nsubjpass"}


def extract_semantic_roles(text: str) -> list[dict[str, Any]]:
    """Extract agent / action / patient frames from *text* using dep-tree
    rules.

    Returns a list of dicts (one per sentence) with keys ``sentence``,
    ``agent``, ``action``, ``patient``, ``entities``.
    """
    nlp = get_spacy()
    if nlp:
        return _extract_roles_spacy(nlp, text)
    return _extract_roles_nltk(text)


def _extract_roles_spacy(nlp: Any, text: str) -> list[dict[str, Any]]:
    doc = nlp(text)
    frames: list[dict[str, Any]] = []
    for sent in doc.sents:
        root = None
        for tok in sent:
            if tok.dep_ == "ROOT":
                root = tok
                break
        if root is None:
            continue

        frame: dict[str, Any] = {
            "sentence": sent.text.strip(),
            "agent": "",
            "action": root.text,
            "patient": "",
            "entities": [],
        }

        # FIX: Collect all agents; prefer the primary nsubj (closest to ROOT)
        agents: list[tuple[int, str]] = []
        for tok in sent:
            if tok.dep_ in AGENT_DEPS:
                dist = abs(tok.head.i - tok.i)
                agents.append((dist, " ".join(t.text for t in tok.subtree)))
            if tok.dep_ == "dobj" and tok.head == root:
                frame["patient"] = " ".join(t.text for t in tok.subtree)
            if tok.dep_ == "pobj":
                head = tok.head
                if head.dep_ == "prep" and head.head == root and not frame["patient"]:
                    frame["patient"] = (
                        head.text + " "
                        + " ".join(t.text for t in tok.subtree)
                    )

        if agents:
            agents.sort(key=lambda x: x[0])
            frame["agent"] = agents[0][1]

        for ent in sent.ents:
            frame["entities"].append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            })

        frames.append(frame)
    return frames


def _extract_roles_nltk(text: str) -> list[dict[str, Any]]:
    """NLTK fallback for SRL (heuristic: first verb = action)."""
    from nltk import pos_tag

    sentences = sent_tokenize(text)
    frames: list[dict[str, Any]] = []
    for sent in sentences:
        tokens = word_tokenize(sent)
        tagged = pos_tag(tokens)

        agent = ""
        action = ""
        patient = ""
        found_verb = False
        pre_verb: list[str] = []
        post_verb: list[str] = []

        for word, tag in tagged:
            if tag.startswith("VB") and not found_verb:
                action = word
                found_verb = True
            elif not found_verb and tag.startswith(("NN", "PRP")):
                pre_verb.append(word)
            elif found_verb and tag.startswith(("NN", "PRP")):
                post_verb.append(word)

        frames.append({
            "sentence": sent,
            "agent": " ".join(pre_verb),
            "action": action,
            "patient": " ".join(post_verb),
            "entities": [],
        })
    return frames


# ---------------------------------------------------------------------------
# Unified semantic analysis (spec-required function)
# ---------------------------------------------------------------------------

def semantic_analysis(
    sentence: str,
    sentence_parse: Any = None,
) -> SemanticFrame:
    """Run NER + SRL + WSD on a single sentence and return a SemanticFrame.

    Parameters
    ----------
    sentence : str
        A single sentence.
    sentence_parse : SentenceParse or None
        Ignored for now (SRL uses its own spaCy pass); kept for interface
        compatibility.

    Returns
    -------
    SemanticFrame
    """
    # NER
    entities = extract_entities(sentence)

    # SRL (takes single sentence but returns list-of-1)
    roles_list = extract_semantic_roles(sentence)
    if roles_list:
        r = roles_list[0]
        agent = r["agent"] or None
        action = r["action"] or None
        patient = r["patient"] or None
    else:
        agent = action = patient = None

    # WSD
    wsd_results = disambiguate(sentence)
    word_senses: dict[str, str] = {
        w["word"]: w["sense"] for w in wsd_results
    }

    return SemanticFrame(
        sentence=sentence,
        agent=agent,
        action=action,
        patient=patient,
        entities=entities,
        word_senses=word_senses,
    )


if __name__ == "__main__":
    import json
    from dataclasses import asdict

    test = "John went to the bank to deposit his money."
    frame = semantic_analysis(test)
    print(json.dumps(asdict(frame), indent=2, default=str))
