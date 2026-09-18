"""
Stage 5 — summary table generator.

Runs the full pipeline on all 10 test samples and produces a summary table
via pandas, exported to both Markdown (stdout) and CSV (``data/summary.csv``).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any

# Ensure project root is importable
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pandas as pd

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


def run_on_samples(
    samples_dir: str | None = None,
) -> tuple[pd.DataFrame, list[tuple[str, PipelineResult]]]:
    """Run the pipeline on every ``.txt`` file in *samples_dir*.

    Returns
    -------
    tuple[pd.DataFrame, list[tuple[str, PipelineResult]]]
        The summary DataFrame and a list of ``(filename, result)`` pairs.
    """
    if samples_dir is None:
        samples_dir = _find_samples_dir()
    samples_dir = os.path.abspath(samples_dir)

    sample_files = sorted(
        f for f in os.listdir(samples_dir) if f.endswith(".txt")
    )

    rows: list[dict[str, Any]] = []
    all_results: list[tuple[str, PipelineResult]] = []

    for fname in sample_files:
        filepath = os.path.join(samples_dir, fname)
        with open(filepath, encoding="utf-8") as fh:
            text = fh.read().strip()

        t0 = time.perf_counter()
        result = process(text)
        elapsed = time.perf_counter() - t0
        all_results.append((fname, result))

        rows.append({
            "sample_id": fname,
            "num_spelling_corrections": len(result.corrections),
            "num_entities": sum(
                len(f.entities) for f in result.semantic_frames
            ),
            "num_semantic_frames": len(result.semantic_frames),
            "num_wsd": sum(
                len(f.word_senses) for f in result.semantic_frames
            ),
            "num_coref_chains": len(result.coref_chains),
            "num_discourse_relations": len(result.discourse_relations),
            "num_indirect_requests": len(result.pragmatic_notes),
            "time_s": round(elapsed, 2),
        })
        logger.info("Processed %s in %.2fs", fname, elapsed)

    df = pd.DataFrame(rows)
    return df, all_results


def print_summary_table(df: pd.DataFrame) -> None:
    """Print the summary table in Markdown format."""
    print("\n" + "=" * 90)
    print("PIPELINE SUMMARY TABLE")
    print("=" * 90)
    print(df.to_markdown(index=False))
    print()

    # Totals row
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if "time_s" in numeric_cols:
        numeric_cols.remove("time_s")
    totals = df[numeric_cols].sum()
    print("TOTALS:")
    for col in numeric_cols:
        print(f"  {col}: {int(totals[col])}")
    print()


def save_summary_csv(df: pd.DataFrame, path: str | None = None) -> str:
    """Export the summary DataFrame to CSV.

    Returns the output path.
    """
    if path is None:
        path = os.path.join(_PROJECT_ROOT, "data", "summary.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Summary CSV written to %s", path)
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    print("Running pipeline on all test samples …")
    print("(This may take a minute on the first run while models load)\n")

    df, all_results = run_on_samples()
    print_summary_table(df)

    csv_path = save_summary_csv(df)
    print(f"Summary CSV saved to: {csv_path}\n")

    # Show detailed results for first 3 samples
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
