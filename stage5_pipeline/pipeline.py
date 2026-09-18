"""
Stage 5 — pipeline wrapper and summary table (re-exports from top-level).

This module delegates to the top-level ``pipeline.py`` for the actual
``process()`` function and provides the summary table generator.
"""

import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import process, PipelineResult, print_results  # noqa: F401

__all__ = ["process", "PipelineResult", "print_results"]
