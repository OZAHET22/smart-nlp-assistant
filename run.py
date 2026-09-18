#!/usr/bin/env python
"""
Smart Reading & Writing Assistant — main entry point.

Usage
-----
    python run.py                              # process all 10 samples + summary table
    python run.py --input test_samples/sample_01.txt   # process a single file
    python run.py --json --input sample.txt    # structured JSON output
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict

# Ensure project root is importable
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from pipeline import process, PipelineResult, print_results


def _find_samples_dir() -> str:
    """Locate the test_samples directory."""
    candidates = [
        os.path.join(_PROJECT_ROOT, "test_samples"),
        os.path.join(_PROJECT_ROOT, "data", "test_samples"),
    ]
    for d in candidates:
        if os.path.isdir(d):
            return os.path.abspath(d)
    raise FileNotFoundError(
        f"Cannot find test_samples directory. Searched: {candidates}"
    )


def run_single(path: str, as_json: bool = False) -> None:
    """Process a single file and display results."""
    with open(path, encoding="utf-8") as fh:
        raw_text = fh.read().strip()

    result = process(raw_text)

    if as_json:
        out = asdict(result)
        out["original_text"] = raw_text
        print(json.dumps(out, indent=2, default=str))
    else:
        print_results(result, raw_text)


def run_all_samples() -> None:
    """Process all 10 test samples, show detailed output and summary table."""
    samples_dir = _find_samples_dir()
    sample_files = sorted(f for f in os.listdir(samples_dir) if f.endswith(".txt"))

    print("=" * 70)
    print("  SMART READING & WRITING ASSISTANT — NLP PIPELINE")
    print("  Processing all test samples …")
    print("=" * 70)
    print()

    summary_rows: list[dict] = []
    t_total = time.perf_counter()

    for fname in sample_files:
        filepath = os.path.join(samples_dir, fname)
        with open(filepath, encoding="utf-8") as fh:
            raw_text = fh.read().strip()

        print(f"\n{'#' * 70}")
        print(f"  FILE: {fname}")
        print(f"{'#' * 70}")

        t0 = time.perf_counter()
        result = process(raw_text)
        elapsed = time.perf_counter() - t0

        print_results(result, raw_text)
        print(f"  [processed in {elapsed:.2f}s]\n")

        summary_rows.append({
            "Sample": fname,
            "Spelling Corrections": len(result.corrections),
            "Entities": sum(len(f.entities) for f in result.semantic_frames),
            "Coref Chains": len(result.coref_chains),
            "Discourse Relations": len(result.discourse_relations),
            "WSD": sum(len(f.word_senses) for f in result.semantic_frames),
            "Indirect Requests": len(result.pragmatic_notes),
        })

    # Print summary table
    total_time = time.perf_counter() - t_total
    print("\n" + "=" * 90)
    print("PIPELINE SUMMARY TABLE")
    print("=" * 90)

    # Header
    cols = list(summary_rows[0].keys())
    header = f"| {'| '.join(f'{c:<22s}' for c in cols)}|"
    sep = f"|{'|'.join('-' * 23 for _ in cols)}|"
    print(header)
    print(sep)

    # Rows
    for row in summary_rows:
        vals = []
        for c in cols:
            v = row[c]
            vals.append(f"{v:<22}" if isinstance(v, str) else f"{v:<22d}")
        print(f"| {'| '.join(vals)}|")

    # Totals
    print(sep)
    totals = ["TOTALS"]
    for c in cols[1:]:
        totals.append(str(sum(row[c] for row in summary_rows)))
    print(f"| {'| '.join(f'{t:<22s}' for t in totals)}|")
    print("=" * 90)
    print(f"\nTotal processing time: {total_time:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smart Reading & Writing Assistant — NLP Pipeline",
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to a single text file to process. "
             "If omitted, all 10 test samples are processed.",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output structured JSON instead of human-readable text",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    if args.input:
        run_single(args.input, as_json=args.json)
    else:
        run_all_samples()


if __name__ == "__main__":
    main()
