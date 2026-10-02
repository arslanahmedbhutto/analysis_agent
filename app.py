"""
InsightAgent AI - Advanced Autonomous Data Analysis Suite
Features: Multi-Provider (Ollama, Groq, Gemini, OpenAI), Interactive Plotly Visualizations,
1-Click Automated EDA Audit, In-Chat Data Cleaning & CSV/Excel Export, and Executive Brief Generation.
"""

import os
import io
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from agent import (
    DataAnalysisAgent,
    get_ollama_models,
    is_ollama_running,
    get_groq_models,
    get_xai_models,
)
from sample_data import generate_sample_ecommerce_data
from executor import execute_analysis_code
try:
    from eda import run_automated_eda, get_smart_prompts
except ImportError:
    import importlib
    import eda
    importlib.reload(eda)
    from eda import run_automated_eda, get_smart_prompts

from report_generator import generate_executive_html_report

# Set page configuration
st.set_page_config(
    page_title="InsightAgent AI | Autonomous Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Modern, Premium SaaS Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0 1.25rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    }
    .brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #1E293B 0%, #4F46E5 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 2px;
    }
    .brand-badge {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.1));
        color: #4F46E5;
        border: 1px solid rgba(79, 70, 229, 0.2);
    }

    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 4px 12px rgba(0, 0, 0, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.08);
        border-color: #CBD5E1;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 2px;
    }

    .hero-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
        border: 1px solid #E0E7FF;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px -2px rgba(79, 70, 229, 0.06);
    }
    .hero-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1E1B4B;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    .hero-desc {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
        max-width: 780px;
        margin-bottom: 20px;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        font-size: 0.88rem;
        color: #334155;
    }
    .feature-icon {
        background: #FFFFFF;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        flex-shrink: 0;
    }

    .badge-online {
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .badge-offline {
        background-color: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    .chart-card {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin: 14px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .chart-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #F1F5F9;
        font-weight: 600;
        font-size: 0.9rem;
        color: #334155;
    }

    .terminal-box {
        background: #0F172A;
        color: #38BDF8;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        line-height: 1.5;
        overflow-x: auto;
        border: 1px solid #1E293B;
    }

    .transformation-banner {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 1px solid #6EE7B7;
        border-radius: 10px;
        padding: 12px 16px;
        color: #065F46;
        margin: 10px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = ""

# Determine Ollama Status
ollama_active = is_ollama_running()

# Sidebar Configuration
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
        <span style="font-size: 26px;">⚡</span>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; color: #1E293B;">Engine Settings</div>
            <div style="font-size: 0.78rem; color: #64748B;">Multi-Provider Support</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    provider = st.selectbox(
        "AI Engine / Provider",
        options=[
            "Local (Ollama) - Free & Offline",
            "xAI Grok (console.x.ai)",
            "Groq Cloud (console.groq.com)",
            "Google Gemini",
            "OpenAI",
            "LM Studio / Custom Local"
        ],
        index=0,
        help="Select Local Ollama to run 100% free offline. Select xAI Grok or Groq Cloud for ultra-fast cloud performance."
    )
    
    api_key = ""
    model_choice = ""
    custom_url = ""

    if "Ollama" in provider:
        if ollama_active:
            st.markdown('<span class="badge-online">● Ollama Engine Connected</span>', unsafe_allow_html=True)
            installed_models = get_ollama_models()
            if installed_models:
                default_idx = 0
                if "qwen2.5-coder:1.5b" in installed_models:
                    default_idx = installed_models.index("qwen2.5-coder:1.5b")
                model_choice = st.selectbox("Installed Model", options=installed_models, index=default_idx)
            else:
                model_choice = st.text_input("Model Name", value="qwen2.5-coder:1.5b")
        else:
            st.markdown('<span class="badge-offline">● Ollama Server Disconnected</span>', unsafe_allow_html=True)
            st.caption("Start Ollama using: `ollama serve`")
            model_choice = st.text_input("Model Name", value="qwen2.5-coder:1.5b")
            
        st.caption("🔒 100% Offline & Free • Zero data transmission")

    elif "xAI Grok" in provider:
        st.markdown('<span class="badge-online">● xAI Grok Frontier Engine</span>', unsafe_allow_html=True)
        env_xai_key = os.getenv("XAI_API_KEY", "")
        api_key = st.text_input(
            "xAI Grok API Key",
            value=env_xai_key,
            type="password",
            placeholder="xai-...",
            help="Get your API key from https://console.x.ai"
        )
        if api_key:
            clean_k = api_key.strip()
            if clean_k.startswith("gsk_"):
                st.warning("⚠️ That key begins with `gsk_`, which is a **Groq Cloud** key. Switch AI Engine to **Groq Cloud**.")
            grok_models = get_xai_models(clean_k)
        else:
            grok_models = ["grok-2-latest", "grok-beta", "grok-2", "grok-vision-beta"]
        model_choice = st.selectbox("Grok Model", options=grok_models, index=0)
        st.caption("🚀 [Get an xAI Grok Key at console.x.ai](https://console.x.ai)")
            
    elif "Groq" in provider:
        st.markdown('<span class="badge-online">● Ultra-Fast Cloud LPUs</span>', unsafe_allow_html=True)
        env_groq_key = os.getenv("GROQ_API_KEY", "")
        api_key = st.text_input(
            "Groq API Key",
            value=env_groq_key,
            type="password",
            placeholder="gsk_...",
            help="Free API key from https://console.groq.com/keys"
        )
        if api_key:
            clean_k = api_key.strip()
            if clean_k.startswith("xai-"):
                st.warning("⚠️ That key begins with `xai-`, which is an **xAI Grok** key from console.x.ai. Switch AI Engine above to **xAI Grok**!")
            groq_models = get_groq_models(clean_k)
        else:
            groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        model_choice = st.selectbox("Groq Model", options=groq_models, index=0)
        st.caption("⚡ [Get a Free Groq Cloud Key at console.groq.com](https://console.groq.com/keys)")
        
    elif "Gemini" in provider:
        st.markdown('<span class="badge-online">● Google AI Studio</span>', unsafe_allow_html=True)
        env_gemini_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini API Key",
            value=env_gemini_key,
            type="password",
            placeholder="AIzaSy...",
            help="Free key from https://aistudio.google.com/app/apikey"
        )
        model_choice = st.selectbox(
            "Gemini Model",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        st.caption("✨ [Get a Free Gemini Key](https://aistudio.google.com/app/apikey)")

    elif "OpenAI" in provider:
        env_openai_key = os.getenv("OPENAI_API_KEY", "")
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_openai_key,
            type="password",
            placeholder="sk-proj-..."
        )
        model_choice = st.selectbox(
            "OpenAI Model",
            options=["gpt-4o", "gpt-4o-mini"],
            index=1
        )
        
    elif "LM Studio" in provider or "Custom" in provider:
        custom_url = st.text_input("Base URL", value="http://localhost:1234/v1")
        model_choice = st.text_input("Model Name", value="local-model")

    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem;">
        <span style="font-size: 22px;">📁</span>
        <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">Dataset Source</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx", "xls"],
        help="Upload CSV or Excel spreadsheets."
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded_file)
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.dataset_name = uploaded_file.name
            st.success(f"Loaded: `{uploaded_file.name}`")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            
    st.markdown("##### 🧪 Or Pick a Curated Dataset:")
    sample_options = {
        "🇵🇰 Pakistan E-Commerce (500 rows)": ("synthetic", "Pakistan_Ecommerce_Sales (500 orders)"),
        "🏬 Retail Store Sales & Marketing (400 rows)": ("sample_datasets/carseats_retail_sales.csv", "Retail_Store_Sales_Marketing"),
        "📞 IBM Telco Customer Churn (7,043 rows)": ("sample_datasets/telco_customer_churn.csv", "Telco_Customer_Churn"),
        "🌍 Gapminder Global GDP & Life (1,704 rows)": ("sample_datasets/gapminder_global_trends.csv", "Gapminder_Global_GDP"),
        "📈 Apple Stock Financial History (506 rows)": ("sample_datasets/apple_stock_finance.csv", "Apple_Stock_Financial_Trends"),
        "🚢 Titanic Passenger Survival (891 rows)": ("sample_datasets/titanic_survival.csv", "Titanic_Passenger_Survival"),
    }
    selected_sample = st.selectbox("Curated Dataset", options=list(sample_options.keys()), index=0)
    if st.button("🚀 Load Selected Dataset", use_container_width=True):
        source_path, label = sample_options[selected_sample]
        if source_path == "synthetic":
            st.session_state.df = generate_sample_ecommerce_data()
        else:
            st.session_state.df = pd.read_csv(source_path)
        st.session_state.dataset_name = label
        st.rerun()

    st.markdown("---")
    
    # Export Session Report
    if st.session_state.df is not None and st.session_state.messages:
        report_html = generate_executive_html_report(
            dataset_name=st.session_state.dataset_name,
            df=st.session_state.df,
            messages=st.session_state.messages
        )
        st.download_button(
            label="📄 Export Executive Report (HTML)",
            data=report_html,
            file_name=f"Executive_Report_{int(time.time())}.html",
            mime="text/html",
            use_container_width=True
        )

    # Workspace Controls
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_c2:
        if st.button("🗑️ Reset All", use_container_width=True):
            st.session_state.messages = []
            st.session_state.df = None
            st.session_state.dataset_name = ""
            st.rerun()

# Top Header Layout
status_badge_html = (
    '<span class="badge-online">● Local Engine Ready</span>'
    if ollama_active
    else '<span class="badge-offline">● Engine Offline</span>'
)

st.markdown(f"""
<div class="app-header">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);">
            📊
        </div>
        <div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="brand-title">InsightAgent AI</span>
                <span class="brand-badge">v2.5 Autonomous</span>
            </div>
            <div class="brand-subtitle">Interactive Plotly Visualizations • Automated EDA Audit • In-Chat Data Cleaning & Export</div>
        </div>
    </div>
    <div>
        {status_badge_html}
    </div>
</div>
""", unsafe_allow_html=True)

# Main Screen State Management
if st.session_state.df is None:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">Turn Natural Language into Executive Data Intelligence</div>
        <div class="hero-desc">
            InsightAgent inspects your tabular dataset, generates real-time Python code, executes it inside an isolated sandbox, captures statistics & interactive Plotly charts, auto-cleans data, and produces executive business insights—all without hallucinating or overriding your data.
        </div>
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">📊</div>
                <div><b>Interactive Plotly Visuals</b>: Hover tooltips, zoom, pan, and dynamic legends.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🚀</div>
                <div><b>1-Click Auto EDA Audit</b>: Instant statistical profiling, anomaly detection & correlations.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🧹</div>
                <div><b>In-Chat Data Cleaning</b>: Transform, filter, enrich data and export new CSVs on the fly.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🆓</div>
                <div><b>100% Free & Offline</b>: Powered by local Ollama with zero API cost and strict data privacy.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_demo1, col_demo2 = st.columns([1.2, 1])
    with col_demo1:
        st.markdown("### 🧪 Quick 1-Click Datasets (No Upload Needed)")
        st.markdown("Select any curated industry dataset below to test the agent immediately:")
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🇵🇰 Pakistan E-Commerce (500)", use_container_width=True, type="primary"):
                st.session_state.df = generate_sample_ecommerce_data()
                st.session_state.dataset_name = "Pakistan_Ecommerce_Sales (500 orders)"
                st.rerun()
            if st.button("📞 Telco Churn (7,043 rows)", use_container_width=True):
                st.session_state.df = pd.read_csv("sample_datasets/telco_customer_churn.csv")
                st.session_state.dataset_name = "Telco_Customer_Churn (7,043 customers)"
                st.rerun()
            if st.button("📈 Apple Stock Finance (506)", use_container_width=True):
                st.session_state.df = pd.read_csv("sample_datasets/apple_stock_finance.csv")
                st.session_state.dataset_name = "Apple_Stock_Financial_Trends (506 days)"
                st.rerun()

        with btn_c2:
            if st.button("🏬 Retail Store Sales (400)", use_container_width=True):
                st.session_state.df = pd.read_csv("sample_datasets/carseats_retail_sales.csv")
                st.session_state.dataset_name = "Retail_Store_Sales_Marketing (400 stores)"
                st.rerun()
            if st.button("🌍 Global GDP & Life (1,704)", use_container_width=True):
                st.session_state.df = pd.read_csv("sample_datasets/gapminder_global_trends.csv")
                st.session_state.dataset_name = "Gapminder_Global_GDP (1,704 records)"
                st.rerun()
            if st.button("🚢 Titanic Passengers (891)", use_container_width=True):
                st.session_state.df = pd.read_csv("sample_datasets/titanic_survival.csv")
                st.session_state.dataset_name = "Titanic_Passenger_Survival (891 passengers)"
                st.rerun()
            
    with col_demo2:
        st.markdown("### 📁 Or Upload Your Own Data")
        st.markdown("Drag and drop your own `.csv` or `.xlsx` spreadsheet in the sidebar to run custom analytics, correlation studies, and business intelligence on your business metrics.")
        st.info("👈 Use the file uploader in the sidebar to begin with your own dataset.")

else:
    df = st.session_state.df
    rows, cols = df.shape
    missing_count = int(df.isnull().sum().sum())
    memory_kb = df.memory_usage(deep=True).sum() / 1024

    # KPI Summary Cards
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">📊 Dataset Rows</div>
            <div class="kpi-value">{rows:,}</div>
            <div class="kpi-sub">Total records analyzed</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">📑 Columns</div>
            <div class="kpi-value">{cols}</div>
            <div class="kpi-sub">Features & dimensions</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">⚠️ Missing Values</div>
            <div class="kpi-value">{missing_count:,}</div>
            <div class="kpi-sub">{"Clean dataset (0 nulls)" if missing_count == 0 else "Requires imputation"}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">💾 Memory Footprint</div>
            <div class="kpi-value">{memory_kb:.1f} <span style="font-size: 1rem; font-weight: 500;">KB</span></div>
            <div class="kpi-sub">Allocated RAM</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Dataset Workspace Tabs
    with st.expander(f"📁 Dataset Explorer & Auto EDA: **{st.session_state.dataset_name}**", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Automated EDA Audit", "📋 Data Preview", "📈 Statistical Summary", "🏷️ Column Types"])
        
        with tab1:
            st.markdown("### 🚀 Automated Executive EDA Audit")
            eda_results = run_automated_eda(df)
            
            # Show executive findings
            for insight in eda_results["insights"]:
                st.markdown(insight)
                
            st.markdown("---")
            if eda_results["corr_fig"] is not None:
                st.plotly_chart(eda_results["corr_fig"], use_container_width=True)
                
            col_eda1, col_eda2 = st.columns(2)
            if eda_results["distribution_figs"]:
                with col_eda1:
                    st.plotly_chart(eda_results["distribution_figs"][0][1], use_container_width=True)
            if eda_results["category_figs"]:
                with col_eda2:
                    st.plotly_chart(eda_results["category_figs"][0][1], use_container_width=True)
                    
            if eda_results["outlier_summary"]:
                st.markdown("##### 🔍 Detected Outliers (IQR Method):")
                outlier_rows = [
                    {"Column": k, "Outlier Count": v["count"], "Outlier %": f"{v['pct']}%", "Normal Range": f"[{v['lower']} to {v['upper']}]"}
                    for k, v in eda_results["outlier_summary"].items()
                ]
                st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True)

        with tab2:
            st.dataframe(df.head(50), use_container_width=True)
            
            # Download Current Dataset
            csv_buf = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Current Dataset (CSV)",
                data=csv_buf,
                file_name="current_dataset.csv",
                mime="text/csv"
            )
            
        with tab3:
            st.dataframe(df.describe(include="all").T, use_container_width=True)
            
        with tab4:
            col_summary_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Missing Values": df.isnull().sum().values,
                "Missing %": (df.isnull().sum().values / len(df) * 100).round(2),
                "Unique Values": df.nunique().values
            })
            st.dataframe(col_summary_df, use_container_width=True)

    # Quick Prompts / Questions (Dynamically generated based on active dataset)
    st.markdown("##### ⚡ Quick Analysis Prompts:")
    smart_prompts = get_smart_prompts(df, st.session_state.dataset_name)
    q_cols = st.columns(len(smart_prompts))
    quick_prompt = None
    for idx, p_info in enumerate(smart_prompts):
        if q_cols[idx].button(p_info["label"], use_container_width=True, help=p_info["prompt"]):
            quick_prompt = p_info["prompt"]

    # Chat Messages History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"**{message['content']}**")
            else:
                st.markdown(message.get("analysis", ""))
                
                # Render Plotly interactive chart if available
                if message.get("plotly_fig"):
                    st.plotly_chart(message["plotly_fig"], use_container_width=True)
                
                # Render Matplotlib static chart if available
                elif message.get("image_bytes"):
                    st.markdown("""
                    <div class="chart-card">
                        <div class="chart-header">
                            <span>📈 Visualization</span>
                            <span style="font-size: 0.8rem; color: #64748B;">High Resolution • Matplotlib/Seaborn</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(message["image_bytes"], use_container_width=True)
                    st.download_button(
                        label="💾 Download Chart (PNG)",
                        data=message["image_bytes"],
                        file_name="analysis_chart.png",
                        mime="image/png",
                        key=f"dl_{message.get('id', time.time())}"
                    )
                    
                # Render Data Transformation Download Button
                if message.get("data_transformed"):
                    st.markdown(f"""
                    <div class="transformation-banner">
                        <span>✨ <b>Dataset updated!</b> The changes have been saved to your active dataset.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    csv_export = st.session_state.df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Cleaned / Transformed Dataset (CSV)",
                        data=csv_export,
                        file_name="transformed_dataset.csv",
                        mime="text/csv",
                        key=f"dl_df_{message.get('id', time.time())}"
                    )

                # Render Python Code in Expander
                if message.get("code"):
                    with st.expander("🔍 View Generated Python Code"):
                        st.code(message["code"], language="python")
                        if message.get("stdout"):
                            st.markdown("**Console Output:**")
                            st.markdown(f'<div class="terminal-box">{message["stdout"]}</div>', unsafe_allow_html=True)

    # Chat Input Box
    user_query = st.chat_input("Ask any question, request interactive plots, or ask to clean/transform the data...")
    if quick_prompt:
        user_query = quick_prompt

    if user_query:
        if not any(local_p in provider for local_p in ["Ollama", "LM Studio"]) and not api_key:
            st.error(f"Please provide your {provider} API key in the sidebar to proceed.")
            st.stop()

        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(f"**{user_query}**")

        # Assistant Execution
        with st.chat_message("assistant"):
            agent = DataAnalysisAgent(
                provider=provider,
                model=model_choice,
                api_key=api_key,
                custom_base_url=custom_url
            )
            
            status_placeholder = st.empty()
            status_placeholder.info(f"🧠 [{provider} • {model_choice}] Generating & executing Python code...")
            
            start_time = time.time()
            
            history_context = [
                {"role": m["role"], "content": m.get("content", "") if m["role"] == "user" else m.get("analysis", "")}
                for m in st.session_state.messages[:-1]
            ]
            
            try:
                result = agent.run_analysis(
                    query=user_query,
                    df=df,
                    chat_history=history_context
                )
            except Exception as e:
                err_msg = str(e)
                if "model_not_found" in err_msg.lower() or "404" in err_msg:
                    friendly_err = f"💡 **Model Notice:** The selected model (`{model_choice}`) could not be reached on {provider}. Please check the model name or verify access in the sidebar."
                elif "api_key" in err_msg.lower() or "401" in err_msg or "unauthorized" in err_msg.lower():
                    friendly_err = f"💡 **Authentication Notice:** Invalid API key for {provider}. Please check your key in the sidebar."
                elif "connection" in err_msg.lower():
                    friendly_err = f"💡 **Connection Notice:** Could not connect to {provider}. Please check your network or local server."
                else:
                    friendly_err = f"💡 **Analysis Notice:** Unable to complete analysis with {provider} at this time. Please try rephrasing your request or use one of the quick prompts above."
                result = {
                    "code": None,
                    "stdout": None,
                    "error": None,
                    "figure": None,
                    "image_bytes": None,
                    "plotly_fig": None,
                    "modified_df": None,
                    "data_transformed": False,
                    "analysis": friendly_err,
                    "success": True,
                    "attempts": 1
                }
            
            elapsed = time.time() - start_time
            status_placeholder.empty()

            # Render Analysis
            st.markdown(result["analysis"])
            
            # If Plotly figure generated, render interactively
            if result.get("plotly_fig"):
                st.plotly_chart(result["plotly_fig"], use_container_width=True)
                
            # Else if Matplotlib figure generated, render static image
            elif result.get("image_bytes"):
                st.markdown("""
                <div class="chart-card">
                    <div class="chart-header">
                        <span>📈 Visualization</span>
                        <span style="font-size: 0.8rem; color: #64748B;">High Resolution • Matplotlib/Seaborn</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.image(result["image_bytes"], use_container_width=True)
                msg_id = int(time.time() * 1000)
                st.download_button(
                    label="💾 Download Chart (PNG)",
                    data=result["image_bytes"],
                    file_name="analysis_chart.png",
                    mime="image/png",
                    key=f"dl_{msg_id}"
                )
                
            # If Data was Transformed, update session state and show download button
            if result.get("data_transformed") and result.get("modified_df") is not None:
                st.session_state.df = result["modified_df"]
                st.markdown(f"""
                <div class="transformation-banner">
                    <span>✨ <b>Dataset updated!</b> Shape is now: <b>{st.session_state.df.shape[0]:,} rows × {st.session_state.df.shape[1]} columns</b>.</span>
                </div>
                """, unsafe_allow_html=True)
                csv_export = st.session_state.df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned / Transformed Dataset (CSV)",
                    data=csv_export,
                    file_name="transformed_dataset.csv",
                    mime="text/csv",
                    key=f"dl_df_{int(time.time()*1000)}"
                )

            # Render Code in Expander
            if result.get("code"):
                with st.expander(f"🔍 View Generated Python Code ({provider} | {elapsed:.2f}s)"):
                    st.code(result["code"], language="python")
                    if result.get("stdout"):
                        st.markdown("**Console Output:**")
                        st.markdown(f'<div class="terminal-box">{result["stdout"]}</div>', unsafe_allow_html=True)

            # Persist in Session History
            st.session_state.messages.append({
                "id": int(time.time() * 1000),
                "role": "assistant",
                "analysis": result["analysis"],
                "code": result.get("code"),
                "stdout": result.get("stdout"),
                "image_bytes": result.get("image_bytes"),
                "plotly_fig": result.get("plotly_fig"),
                "data_transformed": result.get("data_transformed", False)
            })

