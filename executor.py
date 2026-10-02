"""
Enhanced Python code execution sandbox for Data Analysis Agent.
Safely executes generated Python code on a DataFrame.
Supports Matplotlib, Seaborn, Plotly (interactive), Scikit-Learn, and DataFrame transformations.
"""

import sys
import io
import traceback
import contextlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sklearn


class ExecutionResult:
    def __init__(
        self,
        success: bool,
        stdout: str,
        error: str = None,
        figure=None,
        image_bytes: bytes = None,
        plotly_fig=None,
        modified_df: pd.DataFrame = None,
        data_was_transformed: bool = False
    ):
        self.success = success
        self.stdout = stdout
        self.error = error
        self.figure = figure
        self.image_bytes = image_bytes
        self.plotly_fig = plotly_fig
        self.modified_df = modified_df
        self.data_was_transformed = data_was_transformed


def execute_analysis_code(code: str, df: pd.DataFrame) -> ExecutionResult:
    """
    Executes Python code with access to `df`, `pd`, `np`, `px`, `go`, `plt`, `sns`, `sklearn`.
    Detects if Plotly or Matplotlib figures were generated, and detects if `df` was modified.
    """
    plt.close('all')
    plt.clf()

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    # Pass a copy for execution, but track original shape/columns
    orig_shape = df.shape
    orig_columns = list(df.columns)
    orig_dtypes = df.dtypes.to_dict()
    exec_df = df.copy()

    def custom_show(*args, **kwargs):
        pass

    orig_show = plt.show
    plt.show = custom_show

    sandbox_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "px": px,
        "go": go,
        "sklearn": sklearn,
        "df": exec_df,
        "fig": None,
    }

    fig = None
    image_bytes = None
    plotly_fig = None
    success = False
    error_msg = None
    data_transformed = False
    modified_df_result = None

    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            exec(code, sandbox_globals)
        success = True
    except Exception as e:
        success = False
        error_msg = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    finally:
        plt.show = orig_show

    if success:
        # Check if a Plotly figure was created and stored in 'fig' or created via px
        candidate_fig = sandbox_globals.get("fig")
        if candidate_fig is not None and isinstance(candidate_fig, (go.Figure,)):
            plotly_fig = candidate_fig

        # Check if a Matplotlib figure was created
        try:
            active_fig = plt.gcf()
            if active_fig and len(active_fig.get_axes()) > 0:
                fig = active_fig
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
                img_buf.seek(0)
                image_bytes = img_buf.getvalue()
        except Exception:
            pass

        # Check if DataFrame was transformed (added columns, dropped rows, modified data)
        resulting_df = sandbox_globals.get("df")
        if isinstance(resulting_df, pd.DataFrame):
            shape_changed = resulting_df.shape != orig_shape
            cols_changed = list(resulting_df.columns) != orig_columns
            types_changed = resulting_df.dtypes.to_dict() != orig_dtypes
            
            if shape_changed or cols_changed or types_changed:
                data_transformed = True
                modified_df_result = resulting_df

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
        image_bytes=image_bytes,
        plotly_fig=plotly_fig,
        modified_df=modified_df_result,
        data_was_transformed=data_transformed
    )
