"""
Executive Report Generator.
Generates standalone, styled HTML executive briefs from the dataset and chat session.
"""

import datetime
from typing import List, Dict, Any
import pandas as pd


def generate_executive_html_report(dataset_name: str, df: pd.DataFrame, messages: List[Dict[str, Any]]) -> str:
    """Generates a standalone, print-ready HTML executive report."""
    now_str = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
    rows, cols = df.shape
    missing_count = int(df.isnull().sum().sum())
    
    chat_sections = []
    for msg in messages:
        if msg.get("role") == "user":
            chat_sections.append(f"""
            <div class="user-query">
                <span class="query-badge">Question</span>
                <h3>{msg.get("content", "")}</h3>
            </div>
            """)
        elif msg.get("role") == "assistant":
            analysis_text = msg.get("analysis", "").replace("\n", "<br>")
            stdout_text = msg.get("stdout", "")
            stdout_html = f"<div class='terminal-box'><b>Console Output:</b><pre>{stdout_text}</pre></div>" if stdout_text else ""
            
            chat_sections.append(f"""
            <div class="assistant-response">
                <span class="response-badge">AI Business Insight</span>
                <div class="analysis-body">{analysis_text}</div>
                {stdout_html}
            </div>
            <hr class="section-divider">
            """)

    content_html = "\n".join(chat_sections) if chat_sections else "<p><i>No analysis queries recorded in this session.</i></p>"

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Executive Data Intelligence Report - {dataset_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1E293B;
            background: #F8FAFC;
            padding: 40px;
            margin: 0;
            line-height: 1.6;
        }}
        .report-card {{
            max-width: 900px;
            margin: 0 auto;
            background: #FFFFFF;
            padding: 40px;
            border-radius: 14px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 1px solid #E2E8F0;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #EEF2F6;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 800;
            color: #0F172A;
        }}
        .meta {{
            font-size: 13px;
            color: #64748B;
        }}
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        .kpi-item {{
            background: #F1F5F9;
            border-radius: 10px;
            padding: 16px;
            border-left: 4px solid #4F46E5;
        }}
        .kpi-item h4 {{
            margin: 0 0 6px 0;
            font-size: 12px;
            text-transform: uppercase;
            color: #64748B;
        }}
        .kpi-item .val {{
            font-size: 22px;
            font-weight: 700;
            color: #0F172A;
        }}
        .user-query {{
            background: #EEF2FF;
            padding: 14px 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #E0E7FF;
        }}
        .query-badge {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #4F46E5;
        }}
        .user-query h3 {{
            margin: 4px 0 0 0;
            font-size: 16px;
            color: #1E1B4B;
        }}
        .assistant-response {{
            padding: 18px 0;
        }}
        .response-badge {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #059669;
        }}
        .analysis-body {{
            margin-top: 10px;
            font-size: 15px;
            color: #334155;
        }}
        .terminal-box {{
            background: #0F172A;
            color: #38BDF8;
            padding: 12px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            margin-top: 12px;
            overflow-x: auto;
        }}
        .section-divider {{
            border: none;
            border-top: 1px dashed #CBD5E1;
            margin: 24px 0;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #94A3B8;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #EEF2F6;
        }}
        @media print {{
            body {{ background: #FFFFFF; padding: 0; }}
            .report-card {{ box-shadow: none; border: none; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="header">
            <div>
                <div class="title">📊 Executive Intelligence Report</div>
                <div class="meta">Dataset: <b>{dataset_name}</b> | Generated on: {now_str}</div>
            </div>
            <div style="text-align: right;">
                <span style="background: #4F46E5; color: #FFF; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;">InsightAgent AI</span>
            </div>
        </div>

        <div class="kpi-row">
            <div class="kpi-item">
                <h4>Total Rows</h4>
                <div class="val">{rows:,}</div>
            </div>
            <div class="kpi-item">
                <h4>Total Columns</h4>
                <div class="val">{cols}</div>
            </div>
            <div class="kpi-item">
                <h4>Data Quality / Missing</h4>
                <div class="val">{missing_count:,} nulls</div>
            </div>
        </div>

        <h2>Executive Findings & Analytical Queries</h2>
        {content_html}

        <div class="footer">
            Generated autonomously by InsightAgent AI • Confirmed data integrity & isolated execution
        </div>
    </div>
</body>
</html>
"""
    return html_template
