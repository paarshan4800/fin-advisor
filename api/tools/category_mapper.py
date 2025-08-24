from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any
from utils.logger import setup_logger
from agents.llm import llm
import json
from utils.helper import _load_data_from_handle

logger = setup_logger(__name__)

class CategoryMapperInput(BaseModel):
    handle: str = Field(
        ...,
        description=(
            "REQUIRED. Handle returned by mongo_query_tool. "
            "This handle is used to fetch transaction data from Redis cache. "
            "Without this, the tool cannot analyze categories."
        )
    )

    @model_validator(mode='after')
    def validate_input(self):
        if not self.handle:
            raise ValueError("Field 'handle' is required and cannot be empty.")
        return self
    

def _map_categories(handle: str) -> Dict[str, Any]:

    logger.info("Calling LLM to map transaction categories")

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

    return StructuredTool.from_function(
        name="category_mapper",
        description=(
            "Analyzes transaction data (fetched using the provided handle) "
            "to generate category mappings, identify unnecessary spending patterns,and suggest recommendations. "
            "REQUIRES a valid 'handle' from mongo_query_tool."
        ),
        func=_map_categories,
        args_schema=CategoryMapperInput,
        return_direct=False,
    )
