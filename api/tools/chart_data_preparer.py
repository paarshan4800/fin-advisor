from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Optional, Literal, Union
from utils.logger import setup_logger
from agents.llm import llm
import json
from utils.helper import _coerce_transactions, _load_data_from_handle, normalize_chart_result
from schemas.visualizations import VisualizationRouter

logger = setup_logger(__name__)

class ChartDataInput(BaseModel):
    handle: str = Field(
        ...,
        description=(
            "REQUIRED. Handle returned by mongo_query_tool. "
            "This handle is used to fetch the transaction data from Redis cache. "
            "Without this, the tool cannot prepare chart/table data."
        )
    )
    objective: str = Field(
        ...,
        description=(
            "Objective or intent for visualization, e.g., 'breakdown by category', "
            "'trend over time', 'top merchants by spend'. "
            "This helps the LLM decide grouping/aggregation logic."
        )
    )
    preferred_chart: Optional[str] = Field(
        default=None,
        description='Optional hint for chart type: one of "pie", "bar", "line", "table".'
    )
    category_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional: output from category_mapper containing category_mapping, "
            "unnecessary_patterns, and recommendations."
        )
    )

    @model_validator(mode='after')
    def validate_input(self):
        if not self.handle:
            raise ValueError("Field 'handle' is required and cannot be empty.")
        return self

def _prepare_chart_data(
    handle: str,
    objective: str,
    preferred_chart: Optional[str] = None,
    category_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    logger.info("Preparing chart data with LLM")

    data = _load_data_from_handle(handle)

    if not data:
        return {
            "category_mapping": {},
            "unnecessary_patterns": [],
            "recommendations": [],
            "note": "No transactions available for analysis."
        }

    if isinstance(data, str):
        data = json.loads(data)    

    # Build prompt
    preface = (
        "You are a data visualization assistant. Given transaction-like records, "
        "choose an appropriate representation and aggregate/group as needed to produce chart-ready data."
    )

    guidance = []
    if preferred_chart:
        guidance.append(f'Preferred chart type: "{preferred_chart}".')
    if objective:
        guidance.append(f'Objective: {objective}.')
    if category_result:
        guidance.append(
            "You are also given optional categorization hints (category_mapping) that you MAY use for grouping:\n"
            f"{json.dumps(category_result.get('category_mapping', {}), ensure_ascii=False)}"
        )
    guidance_text = "\n".join(guidance) if guidance else "If unclear, infer a sensible chart/table."

    format_rules = (
        "Output STRICT JSON for ONE visualization ONLY.\n"
        "Allowed schemas:\n"
        "- chart: { type: 'chart', chartType: 'pie'|'bar'|'line', data: [{label, value}], text_summary }\n"
        "- table: { type: 'table', headers: string[], rows: (string|number|boolean|null)[][], text_summary }\n\n"
        "TEXT SUMMARY RULE:\n"
        "Always include a 'text_summary' that is 2–4 full sentences. "
        "It should summarize the main insight, highlight trends or patterns, "
        "and mention notable categories, time ranges, or outliers. "
        "Avoid single-word or vague summaries.\n"
        "Do not include any text outside JSON."
    )
    
    prompt = f"""
        {preface}

        {guidance_text}

        {format_rules}

        Respond ONLY with strict JSON matching one of the schemas (pie/bar/line/table). 
        Output JSON must match the keys exactly.

        Raw data (JSON list of records):
        {json.dumps(data, ensure_ascii=False)}
    """

    try:
        structured_llm = llm.with_structured_output(VisualizationRouter)
        resp = structured_llm.invoke(prompt)
        result = resp.visualization.model_dump()
        logger.debug(f"LLM raw response (chart prep): {result}")

        # Minimal validation: ensure required top-level keys exist
        if "type" not in result:
            raise ValueError("Missing 'type' in LLM response.")
        if result["type"] == "chart":
            if "chartType" not in result:
                raise ValueError("Missing 'chartType' for chart response.")
            if "data" not in result:
                raise ValueError("Missing 'data' for chart response.")
        elif result["type"] == "table":
            if "headers" not in result or "rows" not in result:
                raise ValueError("Missing 'headers' or 'rows' for table response.")
            
        if result.get("type") == "chart":
            result = normalize_chart_result(result, max_buckets=12)

        # Always include a short text_summary to keep UX consistent
        if "text_summary" not in result:
            result["text_summary"] = "Prepared chart/table data."

        return result

    except Exception as e:
        logger.error(f"Chart data preparation failed: {e}")
        # Fallback: return a very basic table so the app can still render something
        headers = sorted({k for row in data for k in row.keys()}) if data else []
        rows = [[row.get(h) for h in headers] for row in data[:20]] if headers else []

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "text_summary": "Showing a basic table fallback due to chart preparation error.",
            "error": str(e),
        }

def get_chart_data_preparer_tool():
    return StructuredTool.from_function(
        name="chart_data_preparer",
        description=(
            "Prepare the FINAL visualization JSON (chart or table). "
            "REQUIRES a valid 'handle' from mongo_query_tool to fetch data from Redis cache. "
            "Optionally accepts an objective (aggregation goal) and preferred_chart type. "
            "Returns STRICT JSON for rendering a pie/bar/line chart or a table."
        ),
        func=_prepare_chart_data,
        args_schema=ChartDataInput,
        return_direct=False,
    )
