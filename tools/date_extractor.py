from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import setup_logger
from agents.llm import llm

logger = setup_logger(__name__)

class DateRangeInput(BaseModel):
    query: str = Field(..., description="Natural-language query to extract a start and end date from")

def _extract_date_range(query: str) -> Dict[str, Any]:
    """Extract date range using LLM"""
    logger.info(f"Extracting date range from: {query}")

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = (
        f"Today is {today}. Extract the start and end date (in YYYY-MM-DD format) "
        f"for the following user query: '{query}'. "
        f"Respond ONLY in JSON format like this:\n"
        f'{{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}}'
    )

    try:
        response = llm.invoke(prompt)
        logger.info(f"LLM raw response: {response.content}")

        # Try parsing the JSON response
        import json
        result = json.loads(response.content)

        # Convert to ISO format with microseconds
        start = datetime.strptime(result["start_date"], "%Y-%m-%d")
        end = datetime.strptime(result["end_date"], "%Y-%m-%d")

        start_iso = start.isoformat(timespec="microseconds")
        end_iso = end.isoformat(timespec="microseconds")

        return {
            "start_date": start_iso,
            "end_date": end_iso,
            "parsed_successfully": True
        }

    except Exception as e:
        logger.error(f"Failed to extract date range with LLM: {e}")
        return {
            "start_date": None,
            "end_date": None,
            "parsed_successfully": False,
            "error": str(e)
        }

def get_date_range_tool() -> StructuredTool:
    """Create date range extraction tool"""

    return StructuredTool.from_function(
        name="date_range_extractor",
        description="Extracts start and end dates from natural language queries",
        func=_extract_date_range,
        args_schema=DateRangeInput,
        return_direct=False,
    )
