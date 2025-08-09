from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Any, List, Union
from utils.logger import setup_logger
from agents.llm import llm
import json

logger = setup_logger(__name__)

class CategoryMapperInput(BaseModel):
    transaction_data: Union[str, List[Dict[str, Any]], Dict[str, Any]] = Field(
        ...,
        description=(
            "User's transactions data as a list of dicts (preferred) or JSON string."
            "Should contain details like merchant, description, amount, date, etc."
        )
    )

def _map_categories(transaction_data: Union[str, List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
    """Tool for mapping and analyzing spending categories using LLM"""

    logger.info("Calling LLM to map transaction categories")

    if isinstance(transaction_data, str):
        transaction_data = json.loads(transaction_data)

    prompt = (
        f"""You are a finance assistant. Analyze the user's transaction data.
        1. Categorize transactions (Food, Shopping, Utilities, etc.)
        2. Identify unnecessary spending patterns
        3. Suggest recommendations to save money
        
        Return output ONLY as a valid JSON object with keys:
        {{
            "category_mapping": {{
                "<Category>": ["Merchant/Description", ...]
                }},
            "unnecessary_patterns": ["..."],
            "recommendations": ["..."]
        }}
        Here is the transaction data (JSON): {transaction_data}
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
    """Create category mapping tool"""

    return StructuredTool.from_function(
        name="category_mapper",
        description="Uses LLM to analyze transactions, categorize them, identify unnecessary spending patterns, and suggest budget improvements.",
        func=_map_categories,
        args_schema=CategoryMapperInput,
        return_direct=False,
    )
