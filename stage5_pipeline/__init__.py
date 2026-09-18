try:
    from .pipeline import process, PipelineResult, print_results
    from .summary_table import run_on_samples, print_summary_table
except ImportError:
    from pipeline import process, PipelineResult, print_results
    from summary_table import run_on_samples, print_summary_table
