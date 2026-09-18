"""
Stage 5 — summary table generator.

Runs the full pipeline on all 10 test samples and produces a summary table,
exported to both Markdown (stdout) and CSV (``data/summary.csv``).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any

# Ensure project root is importable
_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_PROJECT_ROOT = os.path.abspath(_PROJECT_ROOT)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tabulate import tabulate
from pipeline import process, PipelineResult

logger = logging.getLogger(__name__)


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


def run_on_samples(samples_dir: str | None = None):
    """Run the pipeline on every ``.txt`` file in *samples_dir*.

    Returns
    -------
    tuple[list, list[tuple[str, PipelineResult]]]
        The summary rows and a list of ``(filename, result)`` pairs.
    """
    if samples_dir is None:
        samples_dir = _find_samples_dir()
    samples_dir = os.path.abspath(samples_dir)

    sample_files = sorted(
        f for f in os.listdir(samples_dir) if f.endswith(".txt")
    )

    rows = []
    all_results: list[tuple[str, PipelineResult]] = []

    for fname in sample_files:
        filepath = os.path.join(samples_dir, fname)
        with open(filepath, encoding="utf-8") as fh:
            text = fh.read().strip()

        result = process(text)
        all_results.append((fname, result))

        num_corrections = len(result.corrections)
        num_entities = sum(len(f.entities) for f in result.semantic_frames)
        num_coref = len(result.coref_chains)
        num_discourse = len(result.discourse_relations)
        num_wsd = sum(len(f.word_senses) for f in result.semantic_frames)
        num_requests = len(result.pragmatic_notes)
        num_frames = len(result.semantic_frames)

        rows.append([
            fname,
            num_corrections,
            num_entities,
            num_frames,
            num_wsd,
            num_coref,
            num_discourse,
            num_requests,
        ])

    return rows, all_results


def print_summary_table(rows):
    """Print the summary table in a grid format."""
    headers = [
        "Sample",
        "Spelling Fixes",
        "Entities",
        "Sem. Frames",
        "WSD",
        "Coref Chains",
        "Discourse Rels",
        "Indirect Reqs",
    ]
    print("\n" + "=" * 90)
    print("PIPELINE SUMMARY TABLE")
    print("=" * 90)
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print()

    totals = [0] * (len(headers) - 1)
    for row in rows:
        for i in range(1, len(row)):
            totals[i - 1] += row[i]
    total_row = ["TOTALS"] + totals
    print(tabulate([total_row], headers=headers, tablefmt="grid"))
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    print("Running pipeline on all test samples...")
    print("(This will take a minute on the first run while the model loads)\n")
    rows, all_results = run_on_samples()
    print_summary_table(rows)

    print("\nDetailed results for first 3 samples:\n")
    from pipeline import print_results
    samples_dir = _find_samples_dir()
    for fname, result in all_results[:3]:
        print(f"\n{'#' * 70}")
        print(f"FILE: {fname}")
        print(f"{'#' * 70}")
        filepath = os.path.join(samples_dir, fname)
        with open(filepath, encoding="utf-8") as fh:
            raw = fh.read().strip()
        print_results(result, raw)
