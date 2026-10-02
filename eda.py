"""
Automated Exploratory Data Analysis (EDA) Engine.
Performs instant statistical profiling, anomaly detection, correlation analysis,
and generates interactive Plotly visualizations.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def run_automated_eda(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive automated exploratory data analysis on a DataFrame.
    Returns metrics, correlation figures, distribution figures, and an executive brief.
    """
    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = round((missing_cells / total_cells * 100), 2) if total_cells > 0 else 0
    duplicate_rows = int(df.duplicated().sum())
    memory_kb = round(df.memory_usage(deep=True).sum() / 1024, 1)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    # Outlier Detection via IQR
    outlier_summary = {}
    for col in numeric_cols:
        col_series = df[col].dropna()
        if len(col_series) > 10:
            q1 = col_series.quantile(0.25)
            q3 = col_series.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                count = int(((col_series < lower) | (col_series > upper)).sum())
                if count > 0:
                    outlier_summary[col] = {
                        "count": count,
                        "pct": round(count / len(col_series) * 100, 1),
                        "lower": round(lower, 2),
                        "upper": round(upper, 2)
                    }

    # Correlation Analysis
    corr_fig = None
    strong_corrs = []
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr().round(2)
        corr_fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis",
            title="Interactive Feature Correlation Matrix"
        )
        corr_fig.update_layout(
            margin=dict(l=40, r=40, t=50, b=40),
            font=dict(family="Plus Jakarta Sans, sans-serif")
        )

        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                c1, c2 = numeric_cols[i], numeric_cols[j]
                val = corr_matrix.loc[c1, c2]
                if abs(val) >= 0.35 and not np.isnan(val):
                    strong_corrs.append((c1, c2, float(val)))

        strong_corrs.sort(key=lambda x: abs(x[2]), reverse=True)

    # Key Distribution Plots (first 2 numeric columns)
    distribution_figs = []
    sample_numeric = numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols
    for col in sample_numeric:
        fig_dist = px.histogram(
            df,
            x=col,
            marginal="box",
            nbins=30,
            title=f"Distribution & Spread: {col}",
            color_discrete_sequence=["#4F46E5"]
        )
        fig_dist.update_layout(
            margin=dict(l=40, r=40, t=50, b=40),
            font=dict(family="Plus Jakarta Sans, sans-serif")
        )
        distribution_figs.append((col, fig_dist))

    # Top Categorical Breakdowns (first 2 categorical columns)
    category_figs = []
    for col in categorical_cols[:2]:
        val_counts = df[col].value_counts().head(10).reset_index()
        val_counts.columns = [col, "count"]
        fig_cat = px.bar(
            val_counts,
            x=col,
            y="count",
            title=f"Top Categories: {col}",
            color="count",
            color_continuous_scale="Blues"
        )
        fig_cat.update_layout(
            margin=dict(l=40, r=40, t=50, b=40),
            font=dict(family="Plus Jakarta Sans, sans-serif")
        )
        category_figs.append((col, fig_cat))

    # Executive Summary Insights
    insights = []
    if missing_cells == 0:
        insights.append("✅ **Clean Ingestion**: Zero missing values detected across all columns.")
    else:
        insights.append(f"⚠️ **Missing Data Alert**: Found {missing_cells:,} missing cells ({missing_pct}% of total dataset).")

    if duplicate_rows > 0:
        insights.append(f"⚠️ **Duplicate Warning**: {duplicate_rows} duplicate rows detected.")
    else:
        insights.append("✅ **Integrity Verified**: No duplicate records found.")

    if strong_corrs:
        top_pair = strong_corrs[0]
        direction = "positive" if top_pair[2] > 0 else "inverse"
        insights.append(f"📊 **Key Correlation**: `{top_pair[0]}` and `{top_pair[1]}` show a strong {direction} correlation ({top_pair[2]:+.2f}).")

    if outlier_summary:
        col_max_out = max(outlier_summary.items(), key=lambda x: x[1]["count"])
        insights.append(f"🔍 **Outlier Notice**: Column `{col_max_out[0]}` contains {col_max_out[1]['count']} statistical outliers ({col_max_out[1]['pct']}% of records).")

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "memory_kb": memory_kb,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols,
        "corr_fig": corr_fig,
        "strong_corrs": strong_corrs,
        "distribution_figs": distribution_figs,
        "category_figs": category_figs,
        "outlier_summary": outlier_summary,
        "insights": insights,
    }

