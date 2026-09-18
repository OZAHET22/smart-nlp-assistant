# Smart Reading & Writing Assistant

A lightweight NLP pipeline that accepts raw, messy student text and processes it through five classical NLP stages — producing spell corrections, syntactic parses, semantic analysis, discourse relations, and pragmatic inferences — all wired as one continuous, testable system.

## Architecture

```
Raw Text
   ↓
Stage 1 — Spell Checking (Levenshtein + Brown Corpus N-gram)
   ↓
Stage 2 — Syntactic Processing (POS Tagging + Dep Parsing + Custom CYK Parser)
   ↓
Stage 3 — Semantic Analysis (NER + Semantic Roles + Lesk WSD)
   ↓
Stage 4 — Discourse & Pragmatic Processing (Coreference + Discourse Relations + Indirect Requests)
   ↓
Stage 5 — Full Pipeline Assembly → Final Structured Results
```

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download the spaCy English model
python -m spacy download en_core_web_sm

# 3. Download required NLTK resources (Brown corpus, WordNet, etc.)
python download_resources.py
```

## Dependencies

| Package     | Purpose                                        |
|-------------|------------------------------------------------|
| `nltk`      | Brown corpus, WordNet, tokenisation, POS tagging (fallback) |
| `spacy`     | POS tagging, dependency parsing, NER           |
| `pandas`    | Summary table generation and CSV export        |
| `tabulate`  | Formatted table output                         |
| `streamlit` | Web interface (stretch goal)                   |
| `requests`  | Resource downloading                           |
| `pytest`    | Test framework                                 |

**Required spaCy model:** `en_core_web_sm` (installed via `python -m spacy download en_core_web_sm`)

## Running

### Process all 10 test samples with summary table
```bash
python run.py
```

### Process a single text file
```bash
python run.py --input test_samples/sample_01.txt
```

### Structured JSON output
```bash
python pipeline.py --input test_samples/sample_01.txt --json
```

### Generate summary table + CSV export
```bash
python summarize.py
```

### Launch the Streamlit web interface (stretch goal)
```bash
streamlit run app.py
```

### Run all tests
```bash
python -m pytest tests/ -v
```

## Stage Explanations

### Stage 1 — Spell Checking (`stage1_spellcheck/`)

Implements **Levenshtein edit distance from scratch** using a two-row rolling dynamic-programming array (O(min(n,m)) space). Misspelled words are detected by checking against the Brown corpus vocabulary supplemented with modern English terms. Candidate corrections are generated within edit distance ≤ 2 and ranked by a combined score of edit distance, word frequency, and **bigram context probability** from a Brown-trained n-gram model. This context-awareness resolves confusable pairs like "there/their/they're" that pure edit-distance cannot distinguish. Each correction produces a structured diff showing original word, replacement, edit distance, and scoring reason.

### Stage 2 — Syntactic Processing (`stage2_syntax/`)

Uses **spaCy** for library-backed POS tagging and dependency parsing, producing token-level analyses with part-of-speech tags, dependency labels, and head words. Additionally implements a **CYK (Cocke–Younger–Kasami) chart parser from scratch** over a 15-rule context-free grammar covering simple declarative sentences (S→NP VP, NP→DET N, VP→V NP PP, etc.). The CYK parser internally converts the grammar to Chomsky Normal Form and produces parse trees for supported sentences. Complex or unsupported sentences return `None` gracefully with an explanatory message, demonstrating proper out-of-grammar handling.

### Stage 3 — Semantic Analysis (`stage3_semantics/`)

Extracts **named entities** (PERSON, ORG, GPE, DATE, etc.) via spaCy's entity recogniser. Builds **semantic role frames** (agent/action/patient) by walking the dependency tree — `nsubj` → agent, `ROOT` verb → action, `dobj` → patient. Implements **Lesk-style Word Sense Disambiguation** for ambiguous words (bank, bat, light, plant, spring, crane, match, ring) using WordNet gloss and hypernym overlap with sentence context. The algorithm retrieves all candidate synsets, computes word-overlap between context tokens and each definition/example/hypernym gloss, and selects the sense with highest overlap.

### Stage 4 — Discourse & Pragmatic Processing (`stage4_discourse/`)

Resolves **pronoun coreference** using a nearest-compatible-antecedent heuristic with gender/number agreement (he→male, she→female, they→plural, it→neutral). Falls back automatically if `coreferee` is unavailable. Detects **discourse connectives** (however, because, therefore, also, etc.) and classifies them into relation types (contrast, cause, cause_effect, elaboration, temporal, condition). Identifies **indirect speech acts** — polite requests phrased as questions (e.g. "Could you send the file?") — via pattern matching on modal-interrogative openers, with action extraction.

### Stage 5 — Full Pipeline Assembly (`pipeline.py`, `stage5_pipeline/`)

Wires Stages 1–4 into a single `process(raw_text)` call. Stage 2+ runs on the **corrected** text from Stage 1 so downstream parses and semantics operate on clean text. The output is a structured `PipelineResult` dataclass containing `corrected_text`, `corrections`, `sentence_parses`, `semantic_frames`, `coref_chains`, `discourse_relations`, and `pragmatic_notes`. The pipeline handles edge cases gracefully — empty entities return `[]`, unsupported grammar returns `None`, missing models trigger NLTK fallbacks. The summary generator runs all 10 samples and produces per-sample statistics.

## Example Output

```
SPELLING CORRECTIONS:
  assigment -> assignment  (edit_dist=1, edit_distance, score=12.3456)
  freind -> friend  (edit_dist=2, edit_distance, score=13.2100)
  thier -> their  (edit_dist=1, context_ngram, score=-8.5432)

CORRECTED TEXT:
  hey prof i wanted to ask about the assignment ...

PARSE TREES (CYK):
  Sentence: she sent the report
  Tree:
    (S
      (NP (PRP she))
      (VP
        (VBD sent)
        (NP (DT the) (NN report))))

SEMANTIC FRAMES:
  Alice sent the report to Bob.
    agent: Alice, action: sent, patient: the report

WORD SENSE DISAMBIGUATION:
  bank       -> bank.n.01     | financial institution

COREFERENCE CHAINS:
  [PERSON] John -> He -> his

DISCOURSE RELATIONS:
  [contrast    ] 'however' (sent 0 -> 1)
  [cause       ] 'because' (sent 1 -> 2)

INDIRECT REQUESTS:
  [indirect_request] Could you send us the rubric again?
    -> send: us the rubric again
```

## Testing

Run the full test suite:

```bash
python -m pytest tests/ -v
```

The test suite contains **140+ tests** covering:
- **Stage 1:** Levenshtein correctness (11 cases), candidate generation, context-aware correction, diff generation, edge cases (empty input, informal words)
- **Stage 2:** CYK parser valid sentences (3+), CYK rejection of invalid sentences, dependency parsing on all 10 samples
- **Stage 3:** Lesk WSD for bank/bat/light in different contexts, NER extraction, SemanticFrame generation on all 10 samples
- **Stage 4:** Coreference chain resolution, discourse connective detection (however/because/therefore/moreover), pragmatic inference (5 positive + 4 negative cases)
- **Pipeline:** End-to-end processing of all 10 samples, field validation, aggregate non-zero checks, JSON serialisability

## Dataset

The `test_samples/` directory contains **10 anonymised, realistic text samples** that mimic messy student writing. Each sample deliberately includes:

| Sample | Key Features |
|--------|-------------|
| sample_01 | Typos (assigment, freind, togehter), confusables (thier), indirect request |
| sample_02 | Ambiguous "bank" (river vs financial), typos (deposite, accross, anoying) |
| sample_03 | Ambiguous "light", discourse connectives (however, because), coreference (she→Sarah) |
| sample_04 | Indirect request (could you plz), typos (heared, importent, lerning) |
| sample_05 | Ambiguous "bat" (animal vs sports), discourse (because, therefore) |
| sample_06 | Coreference (John→he), confusables (their/there), typos (grocerys, finaly) |
| sample_07 | Discourse (meanwhile, because), indirect request, typos (completly, havent) |
| sample_08 | Typos (libary, freezeing, reconize), discourse (although) |
| sample_09 | Named entities (Dr. Smith), discourse (however, because), coreference |
| sample_10 | Indirect request (could you look into it), typos (explane, submited, becuse) |

## Demo

For a **5-minute demonstration**, use the following flow:

1. **Show raw input** — display sample_01.txt (messy student email)
2. **Stage 1 demo** — run `python run.py --input test_samples/sample_01.txt` and walk through spell corrections with edit distances
3. **Stage 2 demo** — point out POS tags, dependency parse, and CYK parse tree output
4. **Stage 3 demo** — show NER entities, semantic roles (agent/action/patient), and WSD results
5. **Stage 4 demo** — show coreference chains, discourse relations, and indirect request detection
6. **Full pipeline** — run `python run.py` to process all 10 samples and show the summary table
7. **Stretch goal** — launch `streamlit run app.py` to show the interactive web interface

For the demo script with detailed talking points, see [`demo/script.md`](demo/script.md).

## Project Structure

```
smart_assistant/
├── stage1_spellcheck/
│   ├── __init__.py
│   ├── edit_distance.py      # Levenshtein from scratch (rolling array)
│   ├── ngram_model.py        # Bigram LM from Brown corpus
│   └── spellchecker.py       # Candidate generation + context-aware correction
├── stage2_syntax/
│   ├── __init__.py
│   ├── pos_tagger.py         # spaCy/NLTK POS tagging
│   ├── dependency_parser.py  # spaCy dependency parsing
│   ├── grammar.py            # 15-rule CFG definition
│   └── cyk_parser.py         # CYK parser from scratch
├── stage3_semantics/
│   ├── __init__.py
│   ├── ner.py                # Named Entity Recognition
│   ├── srl.py                # Semantic Role Labelling
│   └── wsd.py                # Lesk-style Word Sense Disambiguation
├── stage4_discourse/
│   ├── __init__.py
│   ├── coref.py              # Heuristic coreference resolution
│   ├── discourse_relations.py # Connective detection + relation typing
│   └── pragmatics.py         # Indirect request detection
├── stage5_pipeline/
│   ├── __init__.py
│   ├── pipeline.py           # Stage 5 wrapper (delegates to top-level)
│   └── summary_table.py      # Summary table generator
├── tests/
│   ├── test_stage1.py
│   ├── test_stage2.py
│   ├── test_stage3.py
│   ├── test_stage4.py
│   └── test_pipeline.py
├── test_samples/              # 10 messy text samples
├── pipeline.py                # Full pipeline: process(raw_text)
├── run.py                     # Main entry point
├── summarize.py               # Batch processing + summary CSV
├── app.py                     # Streamlit web interface (stretch goal)
├── utils.py                   # Shared spaCy singleton
├── download_resources.py      # NLTK/spaCy resource downloader
├── requirements.txt
└── README.md
```

## Stretch Goal

A **Streamlit web interface** is available via `streamlit run app.py`. It provides:
- Live spell-check tab with autocomplete-as-you-type corrections
- Full pipeline tab that processes text through all 4 stages
- Visual display of parse trees, entities, semantic roles, and discourse analysis
