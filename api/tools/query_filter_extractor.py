from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import setup_logger
from agents.llm import llm  # shared LLM config

import json

logger = setup_logger(__name__)

class QueryFilterInput(BaseModel):
    query: str = Field(..., description="The user's natural language question to extract filters from")

# Format dates to ISO with microseconds if present
def to_iso(date_str):
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.isoformat(timespec="microseconds")
    return None

def _extract_filters(query: str) -> Dict[str, Any]:
    """Extract query filters using LLM"""
    logger.info(f"Extracting structured filters from query: {query}")

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = (
        f"Today is {today}.\n"
        f"From the following user query, extract as many filters as possible and respond ONLY in this JSON format:\n"
        f'{{\n'
        f'  "start_date": "YYYY-MM-DD",\n'
        f'  "end_date": "YYYY-MM-DD",\n'
        f'  "transaction_mode": "Card" | "UPI" | "BankTransfer" | null,\n'
        f'  "currency": "INR" | "USD" | null,\n'
        f'  "amount_min": number | null,\n'
        f'  "amount_max": number | null,\n'
        f'  "status": "success" | "failed" | "refunded" | null\n'
        f'}}\n\n'
        f"If a value is not mentioned in the query, set it to null. Query: '{query}'"
    )

    try:
        response = llm.invoke(prompt)
        logger.info(f"LLM raw response: {response.content}")

        result = json.loads(response.content)

        result["start_date"] = to_iso(result.get("start_date"))
        result["end_date"] = to_iso(result.get("end_date"))

        return {
            "parsed_successfully": True,
            **result
        }

    except Exception as e:
        logger.error(f"Failed to extract filters with LLM: {e}")
        return {
            "parsed_successfully": False,
            "error": str(e),
            "start_date": None,
            "end_date": None,
            "transaction_mode": None,
            "currency": None,
            "amount_min": None,
            "amount_max": None,
            "status": None
        }


def get_query_filter_extractor_tool() -> StructuredTool:
    """Create structured query filter extraction tool"""

    return StructuredTool.from_function(
        name="query_filter_extractor",
        description=(
            "Extracts structured filters from user query including: start_date, end_date, "
            "transaction_mode, currency, amount_min, amount_max, status. "
            "Dates must be in YYYY-MM-DD. Response is JSON."
        ),
        func=_extract_filters,
        args_schema=QueryFilterInput,
        return_direct=False,
    )
