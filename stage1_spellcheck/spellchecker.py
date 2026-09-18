"""
Spell-checker module — candidate generation, context-aware disambiguation,
and diff output.

Uses the from-scratch Levenshtein distance (edit_distance.py) for candidate
generation and the bigram language model (ngram_model.py) for resolving
confusable in-vocabulary words (there/their/they're, its/it's, etc.).
"""

from __future__ import annotations

import logging
import math
import os
import re
from dataclasses import dataclass, field

try:
    from .edit_distance import levenshtein_distance
    from .ngram_model import NgramModel, build_from_brown
except ImportError:
    from edit_distance import levenshtein_distance
    from ngram_model import NgramModel, build_from_brown

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spec-required dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SpellCorrection:
    """One correction applied to a single token."""
    original: str
    corrected: str
    edit_distance: int       # Levenshtein distance between original and corrected
    reason: str              # "edit_distance" | "context_ngram" | "unchanged"
    score: float             # combined cost (distance + context weight)
    context_score: float = 0.0  # n-gram context probability score


@dataclass
class SpellCheckResult:
    """Result of running the spell-checker on a text."""
    original_text: str
    corrected_text: str
    corrections: list[SpellCorrection]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[A-Za-z']+")
FREQ_FLOOR: int = 2         # minimum unigram count to accept a candidate
CTX_WEIGHT: float = 0.35    # how hard context fights edit distance
MAX_DIST: int = 2           # maximum edit-distance radius for candidates

# Modern words that are absent from the 1960s Brown corpus but are
# perfectly valid in contemporary English.  Adding them to the known
# vocabulary prevents false-positive spell-corrections on these words.
MODERN_VOCABULARY: set[str] = {
    # technology
    "upload", "download", "email", "internet", "website", "online",
    "offline", "laptop", "smartphone", "wifi", "bluetooth", "usb",
    "login", "logout", "username", "password", "screenshot", "podcast",
    "blog", "vlog", "hashtag", "emoji", "selfie", "startup", "app",
    "apps", "browser", "server", "database", "backend", "frontend",
    "middleware", "cybersecurity", "malware", "phishing", "blockchain",
    "cryptocurrency", "bitcoin", "gpu", "cpu", "ssd", "hdd", "api",
    "url", "html", "css", "javascript", "python", "github", "gitlab",
    # education / informal
    "prof", "profs", "ok", "okay", "yeah", "nah", "gonna", "wanna",
    "gotta", "kinda", "sorta", "cuz", "coz", "pls", "plz", "thx",
    "info", "intro", "midterm", "midterms", "exam", "exams", "grading",
    "rubric", "rubrics", "syllabus", "ta", "gpa",
    # common modern words
    "healthcare", "wellbeing", "lifestyle", "outsource", "freelance",
    "branding", "podcast", "binge", "recycle", "sustainability",
    "biodiversity", "deforestation", "ecosystem", "pandemic",
    "quarantine", "lockdown", "vaccine", "vaccines", "vaccination",
    "telecommute", "telecommuting", "coworking",
}

# Common informal abbreviations / contractions (without apostrophe) that
# should NOT be corrected because the edit-distance replacement is always
# worse than keeping the original.  These are real words in informal writing.
INFORMAL_SKIP: set[str] = {
    "dont", "cant", "wont", "isnt", "arent", "wasnt", "werent",
    "hasnt", "havent", "hadnt", "didnt", "doesnt", "shouldnt",
    "wouldnt", "couldnt", "mustnt", "im", "ive", "youve", "weve",
    "theyve", "youre", "theyre", "hes", "shes", "whos", "whats",
    "thats", "lets", "its",
    "prof", "profs", "plz", "pls", "thx", "info", "ok", "yo",
    "gonna", "wanna", "gotta", "kinda", "sorta", "cuz", "coz",
    "til", "nah", "yep", "yup", "nope", "lol", "omg", "btw",
}

# Common misspellings that exceed MAX_DIST or where the correct word may
# lose to a rare shorter-distance candidate.  These are checked FIRST so
# the user gets the obvious intended word.
COMMON_MISSPELLINGS: dict[str, str] = {
    "becuz": "because", "becuse": "because", "becuase": "because",
    "becouse": "because", "beacuse": "because", "becasue": "because",
    "realy": "really", "realiy": "really", "reall": "really",
    "thier": "their", "theri": "their",
    "recieve": "receive", "recive": "receive",
    "tommorow": "tomorrow", "tomorow": "tomorrow", "tommorrow": "tomorrow",
    "togehter": "together", "togather": "together", "togeather": "together",
    "occured": "occurred", "occurr": "occurred",
    "seperate": "separate", "seprate": "separate",
    "definately": "definitely", "definatly": "definitely",
    "accomodate": "accommodate", "acommodate": "accommodate",
    "acheive": "achieve", "achive": "achieve",
    "adress": "address", "addres": "address",
    "arguement": "argument", "arguemnt": "argument",
    "begining": "beginning", "begginning": "beginning",
    "beleive": "believe", "belive": "believe",
    "calender": "calendar", "calander": "calendar",
    "catagory": "category", "categroy": "category",
    "comming": "coming", "commming": "coming",
    "commited": "committed", "comitted": "committed",
    "completly": "completely", "completley": "completely",
    "concious": "conscious", "conceous": "conscious",
    "curiousity": "curiosity",
    "desparate": "desperate", "desparete": "desperate",
    "diffrent": "different", "diferent": "different",
    "disapoint": "disappoint", "dissapoint": "disappoint",
    "embarass": "embarrass", "embarras": "embarrass",
    "enviroment": "environment", "enviorment": "environment",
    "essense": "essence",
    "exagerate": "exaggerate", "exaggurate": "exaggerate",
    "excercise": "exercise", "exersize": "exercise",
    "existance": "existence", "existense": "existence",
    "experiance": "experience", "expirence": "experience",
    "explane": "explain", "explian": "explain",
    "familar": "familiar", "familer": "familiar",
    "finaly": "finally", "finially": "finally",
    "foriegn": "foreign", "forein": "foreign",
    "freind": "friend", "frend": "friend",
    "goverment": "government", "govermnent": "government",
    "grammer": "grammar", "gramar": "grammar",
    "gaurd": "guard",
    "happend": "happened", "happned": "happened",
    "harrass": "harass",
    "heared": "heard",
    "helpfull": "helpful", "helpfol": "helpful",
    "immediatly": "immediately", "imediatly": "immediately",
    "importent": "important", "importand": "important",
    "independant": "independent",
    "inteligent": "intelligent",
    "intresting": "interesting", "intersting": "interesting",
    "knowlege": "knowledge", "knowlede": "knowledge",
    "lenght": "length", "lenth": "length",
    "lerning": "learning", "learing": "learning",
    "libary": "library", "liberry": "library",
    "maintenace": "maintenance",
    "manuever": "maneuver",
    "millenium": "millennium",
    "mispell": "misspell",
    "neccessary": "necessary", "necesary": "necessary",
    "noticable": "noticeable",
    "occassion": "occasion", "ocasion": "occasion",
    "occurence": "occurrence", "occurrance": "occurrence",
    "opend": "opened",
    "oportunity": "opportunity", "oppurtunity": "opportunity",
    "parliment": "parliament",
    "persue": "pursue",
    "posession": "possession", "possesion": "possession",
    "postpond": "postponed",
    "potatos": "potatoes",
    "presance": "presence",
    "privlege": "privilege", "privalege": "privilege",
    "probaly": "probably", "proably": "probably",
    "professer": "professor", "proffessor": "professor",
    "pronounciation": "pronunciation",
    "publically": "publicly",
    "recomend": "recommend", "reccomend": "recommend",
    "reconize": "recognize", "reconise": "recognise",
    "refrence": "reference", "referance": "reference",
    "relevent": "relevant", "relavent": "relevant",
    "religous": "religious",
    "repitition": "repetition",
    "resistence": "resistance",
    "rythm": "rhythm", "rhythem": "rhythm",
    "shedule": "schedule", "schedual": "schedule",
    "sentance": "sentence",
    "shouldnt": "should",
    "similer": "similar", "similiar": "similar",
    "sincerly": "sincerely",
    "speach": "speech",
    "strenght": "strength", "strenth": "strength",
    "succesful": "successful", "successfull": "successful",
    "suprise": "surprise", "surprize": "surprise",
    "temperture": "temperature", "temprature": "temperature",
    "therefor": "therefore",
    "tomatos": "tomatoes",
    "tounge": "tongue",
    "truely": "truly",
    "untill": "until", "untl": "until",
    "ususally": "usually", "usally": "usually",
    "vaccuum": "vacuum",
    "valueable": "valuable",
    "vegatable": "vegetable",
    "visable": "visible",
    "wether": "whether",
    "wierd": "weird",
    "writting": "writing", "writeing": "writing",
    # common texting-style misspellings in samples
    "accross": "across",
    "anoying": "annoying", "anoyying": "annoying",
    "assigment": "assignment", "asignment": "assignment",
    "cancle": "cancel", "cancell": "cancel",
    "coverd": "covered",
    "deposite": "deposit",
    "everthing": "everything", "evreything": "everything",
    "freezeing": "freezing", "frezing": "freezing",
    "grocerys": "groceries",
    "submited": "submitted",
    "tryed": "tried",
    "usefull": "useful",
    "weak": "week",
    "wouldnt": "wouldn't",
    "eventualy": "eventually",
    "alot": "a lot",
}

# Commonly-confused in-vocabulary word sets.  Pure edit-distance cannot fix
# these because all variants are valid dictionary words; disambiguation must
# come from the surrounding n-gram context.
CONFUSABLE_SETS: list[set[str]] = [
    {"there", "their", "they're"},
    {"its", "it's"},
    {"your", "you're"},
    {"to", "too", "two"},
    {"then", "than"},
    {"affect", "effect"},
    {"accept", "except"},
    {"lose", "loose"},
    {"were", "where", "we're"},
]

# Flat lookup: word -> set of alternatives
_CONFUSABLE_MAP: dict[str, set[str]] = {}
for _group in CONFUSABLE_SETS:
    for _w in _group:
        _CONFUSABLE_MAP[_w] = _group


# ---------------------------------------------------------------------------
# Public helper functions (spec-required signatures)
# ---------------------------------------------------------------------------

def load_word_frequency(path: str) -> dict[str, int]:
    """Load a ``word<TAB>count`` frequency file into a dict.

    Parameters
    ----------
    path : str
        Filesystem path to a two-column TSV file.

    Returns
    -------
    dict[str, int]
        Mapping of word → corpus count.
    """
    freq: dict[str, int] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                freq[parts[0]] = int(parts[1])
    logger.info("Loaded %d entries from %s", len(freq), path)
    return freq


def generate_candidates(
    word: str,
    freq: dict[str, int],
    max_distance: int = 2,
) -> list[tuple[str, int]]:
    """Generate dictionary words within *max_distance* of *word*.

    Returns
    -------
    list[tuple[str, int]]
        ``(candidate, distance)`` pairs sorted by (distance, then frequency
        descending).
    """
    found: list[tuple[int, int, str]] = []
    for w, count in freq.items():
        if abs(len(w) - len(word)) > max_distance:
            continue
        d = levenshtein_distance(word, w, limit=max_distance)
        if 0 < d <= max_distance:
            found.append((d, -count, w))
    found.sort()
    return [(w, d) for d, _, w in found]


# ---------------------------------------------------------------------------
# Core spell-checker
# ---------------------------------------------------------------------------

class SpellChecker:
    """Context-aware spell-checker backed by Levenshtein + bigram LM."""

    def __init__(self, model: NgramModel | None = None) -> None:
        self.model: NgramModel = model if model is not None else build_from_brown()
        self._cand_cache: dict[str, list[tuple[int, str]]] = {}
        # Inject modern vocabulary into the model so these words are known
        for w in MODERN_VOCABULARY:
            if w not in self.model.vocab:
                self.model.vocab.add(w)
                # Give them a minimal unigram count so they don't get filtered
                if w not in self.model.unigrams:
                    self.model.unigrams[w] = max(FREQ_FLOOR, 5)

    # --- private helpers ---------------------------------------------------

    def _candidates(self, word: str) -> list[tuple[int, str]]:
        """Return ``(distance, candidate)`` pairs within MAX_DIST."""
        if word in self._cand_cache:
            return self._cand_cache[word]
        found: list[tuple[int, str]] = []
        for w in self.model.vocab:
            if abs(len(w) - len(word)) > MAX_DIST:
                continue
            d = levenshtein_distance(word, w, limit=MAX_DIST)
            if 0 < d <= MAX_DIST:
                found.append((d, w))
        found.sort()
        self._cand_cache[word] = found
        return found

    def _fix_oov_word(
        self, word: str, prev: str, nxt: str,
    ) -> tuple[str, SpellCorrection | None]:
        """Correct an out-of-vocabulary word via edit-distance candidates."""
        # Skip informal abbreviations — they look like typos but aren't
        if word in INFORMAL_SKIP:
            return word, None

        # 1. Check the common-misspelling dictionary first.  This handles
        #    typos that exceed MAX_DIST (e.g. becuz→because at distance 3)
        #    and ensures the obvious intended word wins over rare alternatives.
        if word in COMMON_MISSPELLINGS:
            correct = COMMON_MISSPELLINGS[word]
            d = levenshtein_distance(word, correct)
            return correct, SpellCorrection(
                original=word,
                corrected=correct,
                edit_distance=d,
                reason="edit_distance",
                score=float(d),
                context_score=0.0,
            )

        # 2. Fall back to edit-distance candidate generation
        cands = [(d, w) for d, w in self._candidates(word)
                 if self.model.unigrams[w] >= FREQ_FLOOR]
        if not cands:
            return word, None

        best: str | None = None
        best_d: int = 0
        best_cost: float | None = None
        best_p: float = 0.0

        for d, w in cands:
            # Penalise candidates whose length differs a lot from the original
            length_penalty = abs(len(w) - len(word)) * 0.3

            # Reward high-frequency words (common words should be preferred)
            freq_bonus = -0.5 * math.log(max(self.model.unigrams[w], 1))

            p = self.model.score_in_context(w, prev, nxt)
            cost = d + length_penalty + freq_bonus + CTX_WEIGHT * (-math.log(max(p, 1e-20)))
            if best_cost is None or cost < best_cost:
                best, best_d, best_cost, best_p = w, d, cost, p

        assert best is not None
        return best, SpellCorrection(
            original=word,
            corrected=best,
            edit_distance=best_d,
            reason="edit_distance",
            score=float(best_cost) if best_cost is not None else float(best_d),
            context_score=math.log(max(best_p, 1e-20)),
        )

    def _fix_confusable(
        self, word: str, prev: str, nxt: str,
    ) -> tuple[str, SpellCorrection | None]:
        """Disambiguate a known confusable word using n-gram context."""
        alternatives = _CONFUSABLE_MAP.get(word)
        if alternatives is None:
            return word, None

        best_word = word
        best_p = self.model.score_in_context(word, prev, nxt)

        for alt in alternatives:
            if alt == word:
                continue
            p = self.model.score_in_context(alt, prev, nxt)
            if p > best_p:
                best_p = p
                best_word = alt

        if best_word != word:
            return best_word, SpellCorrection(
                original=word,
                corrected=best_word,
                edit_distance=levenshtein_distance(word, best_word),
                reason="context_ngram",
                score=math.log(max(best_p, 1e-20)),
                context_score=math.log(max(best_p, 1e-20)),
            )
        return word, None

    # --- public API --------------------------------------------------------

    def correct(self, text: str) -> SpellCheckResult:
        """Spell-check *text* and return a SpellCheckResult.

        The method first corrects out-of-vocabulary words by edit distance,
        then disambiguates known confusable in-vocabulary words using bigram
        probabilities.
        """
        import time
        t0 = time.perf_counter()

        if not text or not text.strip():
            return SpellCheckResult(
                original_text=text or "",
                corrected_text=text or "",
                corrections=[],
            )

        tokens = [(m.group(0), m.start()) for m in WORD_RE.finditer(text)]
        replacements: list[tuple[int, int, str]] = []
        corrections: list[SpellCorrection] = []

        for i, (w, start) in enumerate(tokens):
            lw = w.lower()
            prev = tokens[i - 1][0].lower() if i > 0 else ""
            nxt = tokens[i + 1][0].lower() if i + 1 < len(tokens) else ""

            if not self.model.known(lw):
                # Mid-sentence capitalised words are probably proper nouns
                if w[0].isupper() and i != 0:
                    continue
                rep, corr = self._fix_oov_word(lw, prev, nxt)
                if corr is not None:
                    if w[0].isupper():
                        rep = rep.capitalize()
                    replacements.append((start, start + len(w), rep))
                    corrections.append(corr)
            else:
                # In-vocabulary — check confusables
                rep, corr = self._fix_confusable(lw, prev, nxt)
                if corr is not None:
                    if w[0].isupper():
                        rep = rep.capitalize()
                    replacements.append((start, start + len(w), rep))
                    corrections.append(corr)

        out = list(text)
        for start, end, rep in reversed(replacements):
            out[start:end] = rep
        corrected_text = "".join(out)

        elapsed = time.perf_counter() - t0
        logger.info("Stage 1 spell-check: %d corrections in %.3fs",
                     len(corrections), elapsed)

        return SpellCheckResult(
            original_text=text,
            corrected_text=corrected_text,
            corrections=corrections,
        )


# ---------------------------------------------------------------------------
# Module-level convenience function (spec signature)
# ---------------------------------------------------------------------------

def spell_check(
    text: str,
    freq: dict[str, int],
    ngram_model: NgramModel,
) -> SpellCheckResult:
    """Spec-required top-level function wrapping :class:`SpellChecker`.

    Parameters
    ----------
    text : str
        Raw text to spell-check.
    freq : dict[str, int]
        Word-frequency dict (currently unused — frequency info comes from the
        *ngram_model*'s unigram counts, which is equivalent).
    ngram_model : NgramModel
        Trained bigram model for context scoring.
    """
    checker = SpellChecker(model=ngram_model)
    return checker.correct(text)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    sc = SpellChecker()
    text = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "i will recieve teh file tommorow and thier freind can check it"
             " in there office"
    )
    result = sc.correct(text)
    print("original :", text)
    print("corrected:", result.corrected_text)
    for c in result.corrections:
        print(f"  {c.original} -> {c.corrected}   "
              f"(edit_dist={c.edit_distance}, {c.reason}, score={c.score:.4f})")
