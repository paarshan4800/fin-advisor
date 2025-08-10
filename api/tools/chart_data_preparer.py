from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Optional, Literal, Union
from utils.logger import setup_logger
from agents.llm import llm
import json
from utils.helper import _coerce_transactions, _load_data_from_handle

logger = setup_logger(__name__)

TableCell = Union[str, int, float, bool, None]

class KVPoint(BaseModel):
    label: str
    value: float

class XYPoint(BaseModel):
    x: float
    y: float
    label: Optional[str] = None

class PieResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["pie"]
    data: List[KVPoint]
    text_summary: str

class BarResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["bar"]
    data: List[KVPoint]
    text_summary: str

class LineResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["line"]
    data: List[KVPoint]
    text_summary: str

class ScatterResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["scatter"]
    data: List[XYPoint]
    text_summary: str

class TableResult(BaseModel):
    type: Literal["table"]
    headers: List[str]
    rows: List[List[TableCell]]
    text_summary: str


ChartOrTableResult = Union[PieResult, BarResult, LineResult, ScatterResult, TableResult]

class VisualizationRouter(BaseModel):
    """Selects and holds the data for a single visualization (chart or table)."""
    visualization: ChartOrTableResult = Field(..., description="The single chart or table object to be rendered.")

class ChartDataInput(BaseModel):
    handle: Optional[str] = Field(
        None,
        description="Handle returned by mongo_query_tool. If provided, data will be loaded from Redis cache."
    )
    raw_data: Optional[List[Dict[str, Any]]] = Field(
        ...,
        description=(
            "(Optional) The raw query results to visualize. Typically a list of transaction documents, "
            "each as a dict with fields like 'initiated_at', 'amount', 'category', 'merchant_name', etc."
            "It should not be sample data"
        )
    )
    preferred_chart: Optional[str] = Field(
        default=None,
        description='Optional preferred chart type: one of "pie", "bar", "line", "scatter", "table".'
    )
    objective: str = Field(
        default=None,
        description=(
            "What we want to show, e.g., 'breakdown by category', 'trend over time', "
            "'top merchants by spend', etc. Helps the LLM decide grouping/aggregation."
        )
    )
    category_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional: output from category_mapper (category_mapping, unnecessary_patterns, recommendations)."
    )

    @model_validator(mode='after')
    def validate_input(self):
        h, td = self.handle, self.raw_data
        if not h and td is None:
            raise ValueError("Provide either 'handle' or 'raw_data'.")
        return self

def _prepare_chart_data(handle: Optional[str] = None,
                        raw_data: Optional[List[Dict[str, Any]]] = None,
                        preferred_chart: Optional[str] = None,
                        objective: str = None,
                        category_result: Optional[Dict[str, Any]] = None,
                        ) -> Dict[str, Any]:
    """
    Use the LLM to transform raw records into a chart-friendly structure.
    The LLM must return STRICT JSON with one of the following shapes:

    For pie:
    {
      "type": "chart",
      "chartType": "pie",
      "data": [{"label": "<string>", "value": <number>}, ...],
      "text_summary": "<one or two lines>"
    }

    For bar:
    {
      "type": "chart",
      "chartType": "bar",
      "data": [{"label": "<string>", "value": <number>}, ...],
      "text_summary": "<one or two lines>"
    }

    For line:
    {
      "type": "chart",
      "chartType": "line",
      "data": [{"label": "YYYY-MM-DD", "value": <number>}, ...],
      "text_summary": "<one or two lines>"
    }

    For scatter:
    {
      "type": "chart",
      "chartType": "scatter",
      "data": [{"x": <number>, "y": <number>, "label": "<optional>"} , ...],
      "text_summary": "<one or two lines>"
    }

    For table:
    {
      "type": "table",
      "headers": ["Col1", "Col2", ...],
      "rows": [[...], [...], ...],
      "text_summary": "<one or two lines>"
    }
    """
    logger.info("Preparing chart data with LLM")

    if handle:
        data = _load_data_from_handle(handle)
    else:
        data = _coerce_transactions(raw_data)

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
        "You are a data visualization assistant. "
        "Given raw transaction-like records, choose an appropriate representation "
        "and aggregate/group as needed."
    )
    constraints = (
        "Respond ONLY with strict JSON (no code fences, no commentary). "
        "Pick the most suitable structure from the schemas described."
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
    
    prompt = f"""
        {preface}
        {guidance_text}
        {constraints}
        Respond ONLY with strict JSON matching one of the schemas (pie/bar/line/scatter/table). 
        Output JSON must match the keys exactly.

        Raw data (JSON list of records):
        {json.dumps(data, ensure_ascii=False)}

        Remember the allowed shapes and keys exactly as specified above.
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

        # Always include a short text_summary to keep UX consistent
        if "text_summary" not in result:
            result["text_summary"] = "Prepared chart/table data."

        return result

    except Exception as e:
        logger.error(f"Chart data preparation failed: {e}")
        # Fallback: return a very basic table so the app can still render something
        headers = sorted({k for row in raw_data for k in row.keys()}) if raw_data else []
        rows = [[row.get(h) for h in headers] for row in raw_data[:20]] if headers else []

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
            "Prepare visualization JSON. REQUIRED: 'raw_data' (the list of Mongo records). "
            "OPTIONAL: 'preferred_chart', 'objective', and 'category_result' (from category_mapper). "
            "Returns strict JSON for a pie/bar/line/scatter chart or a table."
        ),
        func=_prepare_chart_data,
        args_schema=ChartDataInput,
        return_direct=False,
    )
