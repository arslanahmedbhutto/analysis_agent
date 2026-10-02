"""
Multi-Provider Custom Coding Analysis Agent.
Supports Local Ollama (100% Free & Offline), Groq, xAI Grok, Google Gemini, OpenAI, and LM Studio.
Equipped with Plotly interactive charting, Scikit-Learn ML, and Data Transformation.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
import requests
import pandas as pd
from openai import OpenAI
from groq import Groq
from executor import execute_analysis_code, ExecutionResult


def get_ollama_models(host: str = "http://localhost:11434") -> List[str]:
    """Attempts to fetch currently installed models from local Ollama instance."""
    try:
        resp = requests.get(f"{host}/api/tags", timeout=1.5)
        if resp.status_code == 200:
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def is_ollama_running(host: str = "http://localhost:11434") -> bool:
    """Checks if local Ollama daemon is active and responding."""
    try:
        resp = requests.get(f"{host}/api/tags", timeout=1.0)
        return resp.status_code == 200
    except Exception:
        return False


def get_groq_models(api_key: str) -> List[str]:
    """Fetches currently active models available on the user's Groq account."""
    default_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
    if not api_key:
        return default_models
    clean_key = api_key.strip()
    try:
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {clean_key}"},
            timeout=3.0
        )
        if resp.status_code == 200:
            data = resp.json()
            models = [
                m["id"] for m in data.get("data", [])
                if not any(k in m["id"].lower() for k in ["whisper", "guard", "embed", "safeguard"])
            ]
            if models:
                return sorted(models)
    except Exception:
        pass
    return default_models


def get_xai_models(api_key: str) -> List[str]:
    """Fetches currently active models available on the user's xAI Grok account."""
    default_models = ["grok-2-latest", "grok-beta", "grok-2", "grok-vision-beta"]
    if not api_key:
        return default_models
    clean_key = api_key.strip()
    try:
        resp = requests.get(
            "https://api.x.ai/v1/models",
            headers={"Authorization": f"Bearer {clean_key}"},
            timeout=3.0
        )
        if resp.status_code == 200:
            data = resp.json()
            models = [m["id"] for m in data.get("data", [])]
            if models:
                return sorted(models)
    except Exception:
        pass
    return default_models


def get_dataframe_schema(df: pd.DataFrame) -> str:
    """Extracts a structural summary of the DataFrame to guide the LLM."""
    rows, cols = df.shape
    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        nunique = int(df[col].nunique())
        
        if pd.api.types.is_numeric_dtype(df[col]):
            sample_val = f"min: {df[col].min()}, max: {df[col].max()}"
        else:
            top_vals = [str(x) for x in df[col].dropna().unique()[:3]]
            sample_val = f"samples: {', '.join(top_vals)}"
            
        col_info.append(f"- `{col}` ({dtype}): {null_count} nulls, {nunique} unique values. {sample_val}")
    
    col_summary_str = "\n".join(col_info)
    head_preview = df.head(3).to_string(index=False)
    
    schema_text = f"""### Dataset Overview:
- Total Rows: {rows:,}
- Total Columns: {cols:,}

### Columns & Types:
{col_summary_str}

### Sample Rows (First 3 rows only for reference):
```
{head_preview}
```
"""
    return schema_text


class DataAnalysisAgent:
    def __init__(
        self,
        provider: str = "Local (Ollama)",
        model: str = "qwen2.5-coder:1.5b",
        api_key: str = "",
        custom_base_url: str = ""
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key.strip() if api_key else ""
        
        if "Ollama" in provider:
            base_url = custom_base_url or "http://localhost:11434/v1"
            self.client = OpenAI(base_url=base_url, api_key="ollama")
        elif "xAI" in provider or ("Grok" in provider and "Groq" not in provider):
            base_url = "https://api.x.ai/v1"
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
        elif "Groq" in provider:
            self.client = Groq(api_key=self.api_key)
        elif "Gemini" in provider:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
        elif "OpenAI" in provider:
            self.client = OpenAI(api_key=self.api_key)
        elif "LM Studio" in provider or "Custom" in provider:
            base_url = custom_base_url or "http://localhost:1234/v1"
            self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        else:
            self.client = OpenAI(api_key=self.api_key or "dummy")

    def _extract_python_code(self, response_text: str) -> Optional[str]:
        """Extracts python code block from model response."""
        pattern = r"```(?:python)?\s*\n(.*?)```"
        matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
            return max(matches, key=len).strip()
        if "df." in response_text or "plt." in response_text or "px." in response_text or "print(" in response_text:
            return response_text.strip()
        return None

    def run_analysis(
        self,
        query: str,
        df: pd.DataFrame,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Executes autonomous code generation, execution, and self-healing analysis.
        """
        schema_text = get_dataframe_schema(df)
        
        system_prompt = f"""You are an Expert Data Scientist and Python Data Analysis Agent.
You are given a pandas DataFrame named `df` with {len(df):,} rows.

{schema_text}

ENVIRONMENT & LIBRARIES AVAILABLE:
- `df`: The loaded dataset.
- `pd`: pandas
- `np`: numpy
- `px`: plotly.express (RECOMMENDED FOR INTERACTIVE PLOTS)
- `go`: plotly.graph_objects
- `plt`: matplotlib.pyplot
- `sns`: seaborn
- `sklearn`: scikit-learn (for regression, forecasting, clustering, classification)

CRITICAL RULES:
1. PRESERVE DATASET: Do not mock data with `df = pd.DataFrame(...)`. The full dataset is already in `df`.
2. DATA TRANSFORMATION: If the user asks to filter, clean, add columns, or transform data (e.g. 'remove outliers', 'fill nulls', 'add a column profit = ...'):
   - Apply the changes directly to `df` (e.g. `df['profit'] = ...` or `df = df[df['col'] > 0]`).
   - The environment will detect the update and provide a download button for the new dataset!
3. INTERACTIVE VISUALIZATIONS:
   - When generating a chart, PREFER Plotly Express (`px`) and assign it to `fig`:
     e.g., `fig = px.bar(..., title="...")` or `fig = px.line(...)` or `fig = px.scatter(...)`
   - If using matplotlib/seaborn, configure standard plots without calling `plt.show()`.
4. OUTPUT: Always print key summary numbers, tables, or metric calculations using `print(...)`.
5. Format your response strictly with:
   - A brief 1-2 sentence thought/plan.
   - The executable code inside a ```python ``` block.
"""

        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
        messages.append({"role": "user", "content": query})

        executed_code = ""
        exec_result: Optional[ExecutionResult] = None
        attempts = 0

        while attempts <= max_retries:
            attempts += 1
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048,
                )
                raw_response = completion.choices[0].message.content or ""
            except Exception as api_err:
                error_str = str(api_err)
                if "connection" in error_str.lower() and self.provider == "Local (Ollama)":
                    return {
                        "code": None,
                        "stdout": None,
                        "error": error_str,
                        "figure": None,
                        "image_bytes": None,
                        "plotly_fig": None,
                        "modified_df": None,
                        "data_transformed": False,
                        "analysis": "❌ **Could not connect to Ollama.**\n\nPlease ensure Ollama is running (`ollama serve`).",
                        "success": False,
                        "attempts": attempts,
                    }
                raise api_err

            code = self._extract_python_code(raw_response)

            if not code:
                return {
                    "code": None,
                    "stdout": None,
                    "error": None,
                    "figure": None,
                    "image_bytes": None,
                    "plotly_fig": None,
                    "modified_df": None,
                    "data_transformed": False,
                    "analysis": raw_response,
                    "success": True,
                    "attempts": attempts,
                }

            executed_code = code
            exec_result = execute_analysis_code(code, df)

            if exec_result.success:
                break
            else:
                if attempts <= max_retries:
                    messages.append({"role": "assistant", "content": f"```python\n{code}\n```"})
                    messages.append({
                        "role": "user",
                        "content": f"The code resulted in an error:\n{exec_result.error}\nPlease fix the error and provide the updated Python code in ```python```."
                    })

        # Synthesize Executive Analysis
        final_summary = ""
        if exec_result and exec_result.success:
            synthesis_prompt = f"""You are an elite Business Intelligence Analyst.
User Question: "{query}"

Execution Output from Data Code:
{exec_result.stdout if exec_result.stdout else "Code executed successfully without text output."}

Has visual chart generated: {"Yes" if (exec_result.plotly_fig is not None or exec_result.figure is not None) else "No"}
Data transformed: {"Yes" if exec_result.data_was_transformed else "No"}

Provide a clear, executive, well-structured answer to the user:
- Directly answer the question with exact numbers/percentages from the output.
- Highlight 2-3 key takeaways or business insights.
- Provide actionable recommendations if relevant.
- Keep it concise, professional, and formatted in clean markdown bullet points.
"""
            try:
                synth_resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": synthesis_prompt}],
                    temperature=0.2,
                    max_tokens=1024,
                )
                final_summary = synth_resp.choices[0].message.content or ""
            except Exception:
                final_summary = exec_result.stdout or "Analysis complete."
        else:
            final_summary = f"⚠️ Could not execute analysis after {attempts} attempts.\n\n**Error:**\n```\n{exec_result.error if exec_result else 'Unknown error'}\n```"

        return {
            "code": executed_code,
            "stdout": exec_result.stdout if exec_result else "",
            "error": exec_result.error if exec_result and not exec_result.success else None,
            "figure": exec_result.figure if exec_result else None,
            "image_bytes": exec_result.image_bytes if exec_result else None,
            "plotly_fig": exec_result.plotly_fig if exec_result else None,
            "modified_df": exec_result.modified_df if exec_result else None,
            "data_transformed": exec_result.data_was_transformed if exec_result else False,
            "analysis": final_summary,
            "success": exec_result.success if exec_result else False,
            "attempts": attempts,
        }
