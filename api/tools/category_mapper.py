from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Union, Optional
from utils.logger import setup_logger
from agents.llm import llm
import json
from utils.helper import _coerce_transactions, _load_data_from_handle

logger = setup_logger(__name__)

class CategoryMapperInput(BaseModel):
    handle: Optional[str] = Field(
        None,
        description="Handle returned by mongo_query_tool. If provided, data will be loaded from Redis cache."
    )
    transaction_data: Optional[Union[str, List[Dict[str, Any]], Dict[str, Any]]] = Field(
        ...,
        description=(
            "(Optional) User's transactions data as a list of dicts (preferred) or JSON string."
            "Should contain details like merchant, description, amount, date, etc."
            "It should not be sample data"
        )
    )

    @model_validator(mode='after')
    def validate_input(self):
        h, td = self.handle, self.transaction_data
        if not h and td is None:
            raise ValueError("Provide either 'handle' or 'transaction_data'.")
        return self
    

def _map_categories(handle: Optional[str] = None,
                    transaction_data: Optional[Union[str, List[Dict[str, Any]], Dict[str, Any]]] = None,
                    ) -> Dict[str, Any]:
    """Tool for mapping and analyzing spending categories using LLM, sourcing data by handle when available."""

    logger.info("Calling LLM to map transaction categories")

    if handle:
        data = _load_data_from_handle(handle)
    else:
        data = _coerce_transactions(transaction_data)

    if not data:
        return {
            "category_mapping": {},
            "unnecessary_patterns": [],
            "recommendations": [],
            "note": "No transactions available for analysis."
        }

    if isinstance(data, str):
        data = json.loads(data)

    prompt = (
        f"""You are a finance assistant. Analyze the user's transaction data.
        1. Categorize transactions into meaningful spending categories (e.g., Food, Shopping, Utilities, Transport, Rent, Entertainment, Healthcare, Fees, Transfers, Others).
        2. Identify unnecessary spending patterns (duplicate subscriptions, excessive fees, impulse buys, etc.).
        3. Suggest actionable recommendations to save money.
        
        Return output ONLY as a valid JSON object with keys:
        {{
            "category_mapping": {{
                "<Category>": ["Merchant/Description", ...]
                }},
            "unnecessary_patterns": ["..."],
            "recommendations": ["..."]
        }}
        Here is the transaction data (JSON): {data}
        CRITICAL: Respond ONLY with a single JSON object. No code fences or prose.
        """
    )

    try:
        response = llm.invoke(prompt)
        logger.debug(f"LLM raw response: {response.content}")
        return json.loads(response.content)
    except Exception as e:
        logger.error(f"LLM category mapping failed: {e}")
        return {
            "category_mapping": {},
            "unnecessary_patterns": [],
            "recommendations": [],
            "error": str(e)
        }


def get_category_mapper_tool() -> StructuredTool:
    """Create category mapping tool that prefers Redis handle but can accept raw data."""

    return StructuredTool.from_function(
        name="category_mapper",
        description=(
            "Analyzes transactions to produce category mapping, unnecessary spending patterns, and recommendations. "
            "Prefer passing a 'handle' (from mongo_query_tool). Optionally accepts raw 'transaction_data'. Doesn't accept sample data"
        ),
        func=_map_categories,
        args_schema=CategoryMapperInput,
        return_direct=False,
    )
