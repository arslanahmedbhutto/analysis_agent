"""
Python code execution sandbox for Data Analysis Agent.
Safely executes generated Python code on a DataFrame, capturing stdout, errors, and matplotlib/seaborn figures.
"""

import sys
import io
import traceback
import contextlib
import matplotlib
# Use Agg backend for headless / server execution
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class ExecutionResult:
    def __init__(self, success: bool, stdout: str, error: str = None, figure=None, image_bytes: bytes = None):
        self.success = success
        self.stdout = stdout
        self.error = error
        self.figure = figure
        self.image_bytes = image_bytes


def execute_analysis_code(code: str, df: pd.DataFrame) -> ExecutionResult:
    """
    Executes Python code with access to `df`, `pd`, `np`, `plt`, `sns`.
    Captures stdout and any generated matplotlib figure.
    """
    # Clear any previous figures
    plt.close('all')
    plt.clf()

    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    # Create execution namespace
    # Provide a copy of df so code errors don't corrupt the original
    exec_df = df.copy()
    
    # Custom show function that doesn't close the figure
    def custom_show(*args, **kwargs):
        pass

    # Save original plt.show
    orig_show = plt.show
    plt.show = custom_show

    sandbox_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "df": exec_df,
    }

    fig = None
    image_bytes = None
    success = False
    error_msg = None

    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            exec(code, sandbox_globals)
        success = True
    except Exception as e:
        success = False
        error_msg = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    finally:
        plt.show = orig_show

    # Check if a figure was created with plots
    try:
        active_fig = plt.gcf()
        if active_fig and len(active_fig.get_axes()) > 0:
            fig = active_fig
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
            img_buf.seek(0)
            image_bytes = img_buf.getvalue()
    except Exception as fig_err:
        pass

    stdout_text = stdout_capture.getvalue().strip()
    stderr_text = stderr_capture.getvalue().strip()
    combined_output = stdout_text
    if stderr_text and not error_msg:
        combined_output += f"\n[stderr]: {stderr_text}" if combined_output else f"[stderr]: {stderr_text}"

    return ExecutionResult(
        success=success,
        stdout=combined_output,
        error=error_msg,
        figure=fig,
        image_bytes=image_bytes
    )
