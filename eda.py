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


def get_smart_prompts(df: pd.DataFrame, dataset_name: str = "") -> List[Dict[str, str]]:
    """
    Dynamically generates 5 highly relevant, executable analysis prompts
    tailored specifically to the active dataset's columns, types, and domain.
    """
    col_lower_map = {c.lower(): c for c in df.columns}
    cols_lower = set(col_lower_map.keys())
    name_lower = dataset_name.lower()

    # 1. Telco Customer Churn
    if any(k in name_lower for k in ["churn", "telco"]) or ("churn" in cols_lower and "tenure" in cols_lower):
        contract_col = col_lower_map.get("contract", "Contract")
        churn_col = col_lower_map.get("churn", "Churn")
        monthly_col = col_lower_map.get("monthlycharges", col_lower_map.get("monthly_charges", "MonthlyCharges"))
        tenure_col = col_lower_map.get("tenure", "tenure")
        total_col = col_lower_map.get("totalcharges", col_lower_map.get("total_charges", "TotalCharges"))

        return [
            {
                "label": "📊 Churn by Contract",
                "prompt": f"Calculate the churn rate grouped by `{contract_col}` and plot an interactive Plotly bar chart comparing churned vs retained customers."
            },
            {
                "label": "💵 Charges vs Churn",
                "prompt": f"Create an interactive histogram of `{monthly_col}` broken down by `{churn_col}` to see if high-paying customers churn more."
            },
            {
                "label": "⏳ Tenure vs Total Charges",
                "prompt": f"Create an interactive scatter plot of `{tenure_col}` vs `{total_col}` colored by `{churn_col}` to analyze customer lifetime behavior."
            },
            {
                "label": "🧹 Filter High-Risk Churn",
                "prompt": f"Filter the dataset for customers with Month-to-month contracts and monthly charges above the median, and calculate their churn rate."
            },
            {
                "label": "💼 Retention Strategy Brief",
                "prompt": "Provide an executive business summary of key churn drivers, highest-risk customer segments, and actionable retention recommendations."
            }
        ]

    # 2. Stock / Financial Time Series (Apple, etc.)
    if any(k in name_lower for k in ["stock", "apple", "aapl", "finance"]) or ("close" in cols_lower and any(d in cols_lower for d in ["date", "timestamp", "time"])):
        close_col = col_lower_map.get("close", col_lower_map.get("adj close", col_lower_map.get("price", "Close")))
        date_col = col_lower_map.get("date", col_lower_map.get("timestamp", "Date"))
        vol_col = col_lower_map.get("volume", "Volume")
        return [
            {
                "label": "📈 Stock Price Trend",
                "prompt": f"Plot an interactive line chart of `{close_col}` over `{date_col}` with range selector sliders."
            },
            {
                "label": "📊 Trading Volume Peaks",
                "prompt": f"Analyze `{vol_col}` distribution and identify the top 5 highest-volume trading days with their price movements."
            },
            {
                "label": "📉 Moving Averages",
                "prompt": f"Calculate 20-day and 50-day rolling moving averages on `{close_col}` and plot them together interactively."
            },
            {
                "label": "⚡ Return Volatility",
                "prompt": f"Calculate daily percentage returns from `{close_col}` and plot the return volatility distribution."
            },
            {
                "label": "💼 Executive Market Brief",
                "prompt": "Provide an executive investment summary: overall trend, maximum drawdown, price milestones, and key takeaways."
            }
        ]

    # 3. Titanic Passenger Survival
    if any(k in name_lower for k in ["titanic", "passenger", "survival"]) or ("survived" in cols_lower and "pclass" in cols_lower):
        survived_col = col_lower_map.get("survived", "Survived")
        pclass_col = col_lower_map.get("pclass", "Pclass")
        sex_col = col_lower_map.get("sex", "Sex")
        age_col = col_lower_map.get("age", "Age")
        fare_col = col_lower_map.get("fare", "Fare")
        return [
            {
                "label": "🚢 Survival by Class & Gender",
                "prompt": f"Calculate survival rate grouped by `{sex_col}` and `{pclass_col}` and show an interactive grouped bar chart."
            },
            {
                "label": "🎂 Age Distribution vs Survival",
                "prompt": f"Plot an interactive histogram of `{age_col}` comparing passengers who survived vs those who did not."
            },
            {
                "label": "🎟️ Ticket Fare Breakdown",
                "prompt": f"Create an interactive box plot of `{fare_col}` across `{pclass_col}` and check how wealth impacted survival."
            },
            {
                "label": "🧹 Family Survival Metric",
                "prompt": "Create a new column `FamilySize` = SibSp + Parch + 1 and calculate survival rates across different family sizes."
            },
            {
                "label": "💼 Historical Survival Insights",
                "prompt": "Provide an executive statistical breakdown of the primary factors that determined survival on the Titanic."
            }
        ]

    # 4. Gapminder Global Development
    if any(k in name_lower for k in ["gapminder", "gdp", "country"]) or ("lifeexp" in cols_lower and "gdppercap" in cols_lower):
        life_col = col_lower_map.get("lifeexp", "lifeExp")
        gdp_col = col_lower_map.get("gdppercap", "gdpPercap")
        continent_col = col_lower_map.get("continent", "continent")
        year_col = col_lower_map.get("year", "year")
        return [
            {
                "label": "🌍 GDP vs Life Expectancy",
                "prompt": f"Create an interactive scatter plot of `{gdp_col}` vs `{life_col}` colored by `{continent_col}` (log scale for GDP)."
            },
            {
                "label": "📈 Longevity Trends Over Time",
                "prompt": f"Plot the trend of average `{life_col}` over `{year_col}` across each continent with interactive lines."
            },
            {
                "label": "🏆 Top 10 Economies",
                "prompt": f"Find the top 10 countries with the highest `{gdp_col}` in the latest year and show an interactive bar chart."
            },
            {
                "label": "⚖️ Continental Inequality",
                "prompt": f"Compare GDP per capita distributions across `{continent_col}` using interactive box plots."
            },
            {
                "label": "💼 Global Development Brief",
                "prompt": "Provide an executive briefing on global health improvements, wealth disparities, and future outlook."
            }
        ]

    # 5. Carseats Retail Sales
    if any(k in name_lower for k in ["carseats", "retail", "store"]) or ("sales" in cols_lower and "shelveloc" in cols_lower):
        sales_col = col_lower_map.get("sales", "Sales")
        shelf_col = col_lower_map.get("shelveloc", "ShelveLoc")
        price_col = col_lower_map.get("price", "Price")
        ad_col = col_lower_map.get("advertising", "Advertising")
        return [
            {
                "label": "🏪 Sales by Shelf Location",
                "prompt": f"Compare unit `{sales_col}` across `{shelf_col}` quality with an interactive Plotly box plot."
            },
            {
                "label": "🏷️ Price vs Sales Elasticity",
                "prompt": f"Create a scatter plot of `{price_col}` vs `{sales_col}` with trendline to evaluate price elasticity."
            },
            {
                "label": "📺 Advertising ROI",
                "prompt": f"Analyze the correlation and impact of `{ad_col}` budget on unit `{sales_col}`."
            },
            {
                "label": "🧹 High Performer Filter",
                "prompt": f"Filter for top 20% sales stores and analyze their common shelf location and pricing characteristics."
            },
            {
                "label": "💼 Retail Strategy Brief",
                "prompt": "Provide executive recommendations on shelf placement, optimal pricing tiers, and advertising allocation."
            }
        ]

    # 6. E-Commerce (Pakistan / Retail Orders)
    if any(k in name_lower for k in ["ecommerce", "order", "pakistan"]) or (("order_id" in cols_lower or "revenue" in cols_lower) and "city" in cols_lower):
        city_col = col_lower_map.get("city", "city")
        rev_col = col_lower_map.get("revenue", col_lower_map.get("sales", "revenue"))
        channel_col = col_lower_map.get("channel", "channel")
        cat_col = col_lower_map.get("category", col_lower_map.get("product_category", "category"))
        return [
            {
                "label": "🏆 Top Revenue Cities",
                "prompt": f"Which `{city_col}` has the highest total `{rev_col}`? Create an interactive Plotly bar chart."
            },
            {
                "label": "📈 Revenue Trends",
                "prompt": f"Plot an interactive line chart of total `{rev_col}` trend over time with rotated labels."
            },
            {
                "label": "⚖️ Channel Breakdown",
                "prompt": f"Compare sales channels in terms of total `{rev_col}` and average order value."
            },
            {
                "label": "📦 Category Share",
                "prompt": f"Create an interactive pie/donut chart showing `{rev_col}` contribution across `{cat_col}`."
            },
            {
                "label": "💼 Executive Sales Brief",
                "prompt": "Give me an executive summary of business performance with key KPIs and actionable growth strategies."
            }
        ]

    # 7. Generic Fallback for ANY uploaded CSV: dynamically inspect columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in df.select_dtypes(include=['object', 'category', 'string']).columns if df[c].nunique() < 50]
    date_cols = [c for c in df.columns if any(w in c.lower() for w in ['date', 'time', 'year', 'month', 'day'])]

    prompts = []

    # Prompt 1: Overview
    prompts.append({
        "label": "📋 Dataset Overview",
        "prompt": "Provide an executive summary of this dataset: key distributions, main metrics, and what insights can be derived."
    })

    # Prompt 2: Categorical breakdown or top counts
    if categorical_cols and numeric_cols:
        cat = categorical_cols[0]
        num = numeric_cols[0]
        prompts.append({
            "label": f"📊 {cat[:12]} Breakdown",
            "prompt": f"Analyze average `{num}` grouped by `{cat}` and show an interactive Plotly bar chart ranking the top categories."
        })
    elif categorical_cols:
        cat = categorical_cols[0]
        prompts.append({
            "label": f"📊 Top {cat[:12]}",
            "prompt": f"Show the distribution and frequency count of `{cat}` using an interactive horizontal bar chart."
        })
    elif len(numeric_cols) >= 1:
        num = numeric_cols[0]
        prompts.append({
            "label": f"📊 {num[:12]} Distribution",
            "prompt": f"Plot an interactive histogram showing the distribution and outliers of `{num}`."
        })

    # Prompt 3: Time trend or correlation
    if date_cols and numeric_cols:
        d_col = date_cols[0]
        n_col = numeric_cols[0]
        prompts.append({
            "label": f"📈 {n_col[:10]} Trend",
            "prompt": f"Plot an interactive line chart showing the trend of `{n_col}` over `{d_col}`."
        })
    elif len(numeric_cols) >= 2:
        n1, n2 = numeric_cols[0], numeric_cols[1]
        prompts.append({
            "label": f"🔍 {n1[:8]} vs {n2[:8]}",
            "prompt": f"Create an interactive scatter plot of `{n1}` vs `{n2}` to investigate their correlation."
        })
    elif len(numeric_cols) == 1:
        num = numeric_cols[0]
        prompts.append({
            "label": f"📦 {num[:12]} Boxplot",
            "prompt": f"Create an interactive box plot of `{num}` to inspect medians, quartiles, and anomalies."
        })

    # Prompt 4: Data cleaning / Transformation suggestion
    if df.isnull().sum().sum() > 0:
        prompts.append({
            "label": "🧹 Clean Null Values",
            "prompt": "Identify all columns with missing values, handle them with appropriate imputation or filtering, and report the cleaned record count."
        })
    elif numeric_cols:
        primary = numeric_cols[0]
        prompts.append({
            "label": "🎯 Outlier Detection",
            "prompt": f"Identify and isolate statistical outliers in `{primary}` using the IQR method, and visualize them."
        })
    else:
        prompts.append({
            "label": "📑 Variable Summary",
            "prompt": "Calculate frequency tables and summary statistics across the main variables."
        })

    # Prompt 5: Executive insights
    prompts.append({
        "label": "💼 Executive Insights",
        "prompt": "Provide an executive briefing: key takeaways, surprising patterns, and 3 actionable recommendations based on this data."
    })

    return prompts[:5]

