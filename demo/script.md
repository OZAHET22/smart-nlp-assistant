# 5-Minute Demo Script

> **Audience:** anyone watching the demo video recording  
> **Goal:** show the pipeline running live on real messy text, stage by stage

---

## 0:00 – 0:30 — Pitch

> "This is a Smart Reading & Writing Assistant — a lightweight Grammarly-style
> NLP pipeline that takes raw, messy student text and processes it through four
> stages: spell checking, syntactic parsing, semantic analysis, and
> discourse/pragmatic inference. Unlike a single API call, every stage is
> visible and explainable."

---

## 0:30 – 2:00 — Live run on Sample 01

**Sample text (sample_01.txt):**
> "hey prof i wanted to ask about the assigment thats due on friday. me and my
> freind were working on it togehter but we cant figure out the last part. could
> you send us the rubric again? …"

Run command:
```bash
python pipeline.py --input test_samples/sample_01.txt
```

**Narrate as output appears:**

1. **Stage 1 (Spelling diff):**  
   - `assigment` → `assignment` (edit_distance, d=1)  
   - `freind` → `friend` (edit_distance, d=1)  
   - `togehter` → `together` (edit_distance, d=1)  
   - Point out: "The model also checks confusables like *there/their* using
     bigram probabilities — something pure edit-distance can't do."

2. **Stage 2 (Parse tree):**  
   - Show the CYK parse tree for a short sentence that fits the grammar.  
   - Mention: "For complex or informal sentences outside the 15-rule grammar,
     we fall back to spaCy's dependency parser."

3. **Stage 3 (Semantic JSON):**  
   - Show agent/action/patient for "could you send us the rubric".  
   - Note any WSD hits if target words appear.

4. **Stage 4 (Discourse / Pragmatics):**  
   - Highlight the indirect request: "could you send us the rubric again?"  
   - Show `[indirect_request]` output and the paraphrase.

---

## 2:00 – 3:30 — Second sample: n-gram disambiguation & discourse

**Sample text (sample_07.txt):**
> "the meeting yesterday was completly useless … because of this delay several
> clients are unhappy. would it be possible for you to escalate this to the
> director?"

Run:
```bash
python pipeline.py --input test_samples/sample_07.txt
```

**Highlight:**
- **N-gram disambiguation:** if any confusable word appears (e.g. "their" vs
  "there"), show how context probability selects the right form — not edit
  distance.
- **Discourse relation:** `[cause]` for "because of this delay".
- **Indirect request:** "would it be possible for you to escalate…" fires the
  pragmatic rule.

---

## 3:30 – 4:30 — Summary table across all 10 samples

Run:
```bash
python summarize.py
```

Walk through the table:
- Every column should show nonzero counts for at least one sample.
- Point out columns: `num_spelling_corrections`, `num_entities`,
  `num_coref_chains`, `num_discourse_relations`, `num_indirect_requests`.
- The CSV is also saved to `data/summary.csv`.

---

## 4:30 – 5:00 — What worked / known limitations

> **Worked well:**
> - Edit-distance + n-gram combo catches both typos and confusables.
> - Heuristic coreference degrades gracefully without a pretrained model.
> - Discourse connective lookup is simple but catches the most common patterns.

> **Known limitations:**
> - The custom CYK grammar only covers ~15 rules (simple declaratives) — it
>   correctly returns `None` for anything outside it rather than silently failing.
> - The heuristic coref resolver has no semantic understanding of gender for
>   novel proper names, only surface-level cues.
> - WSD Lesk accuracy is limited by vocabulary overlap; rare words may pick the
>   most common WordNet sense instead of the contextually correct one.
