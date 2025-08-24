from langchain.tools import StructuredTool
from utils.logger import setup_logger
from agents.llm import llm
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

logger = setup_logger(__name__)

FIELD_WHITELIST: Set[str] = {
    "_id",
    "transaction_id",
    "user_id",
    "from_account_id",
    "to_account_id",
    "merchant_id",
    "amount",
    "currency",
    "transaction_type",
    "transaction_mode",
    "status",
    "initiated_at",
    "completed_at",
    "failed_at",
    "remarks",
    "description",
    "reference_number",
    "order_id",
    "created_at",
    "updated_at",
}

allowed_fields_sorted = sorted(FIELD_WHITELIST)

DEFAULT_INCLUDE: Set[str] = {"amount", "initiated_at"}

# If you prefer excluding `_id` to reduce payload size, set this True.
EXCLUDE_ID_BY_DEFAULT = False

class ProjectionToolInput(BaseModel):
    query: str = Field(
        ...,
        description="Natural language user query describing what they want to analyze or view.",
    )

class ProjectionChoice(BaseModel):
    fields: List[str] = Field(
        ...,
        description="Minimal list of field names from the transactions schema needed to fulfill the user request.",
    )
    reasoning: str = Field(..., description="Short explanation of why these fields are needed.")

    # @validator("fields")
    # def _dedupe_strip(cls, v):
    #     seen = set()
    #     out = []
    #     for f in v:
    #         if isinstance(f, str):
    #             f2 = f.strip()
    #             if f2 and f2 not in seen:
    #                 seen.add(f2)
    #                 out.append(f2)
    #     if not out:
    #         raise ValueError("No usable fields suggested.")
    #     return out

_parser = JsonOutputParser(pydantic_object=ProjectionChoice)

examples = [
    (
        "Categorize my spendings in the last two months",
        ["amount", "initiated_at", "transaction_type", "transaction_mode", "merchant_id", "description", "remarks", "currency"]
    ),
    (
        "Show failed transfers with reference numbers",
        ["status", "initiated_at", "amount", "reference_number", "transaction_mode", "transaction_type"]
    ),
    (
        "Find big cash withdrawals",
        ["amount", "initiated_at", "transaction_mode", "transaction_type", "remarks"]
    ),
]

few_shot = "\n".join(
    [f"Example {i+1}:\nUser query: {q}\nChoose fields: {fs}\n" for i, (q, fs) in enumerate(examples)]
)

_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a data selection assistant for a MongoDB 'transactions' collection. "
            "Choose the MINIMAL set of fields required to satisfy the user's request.\n"
            "Rules:\n"
            "- ONLY choose from the allowed schema list.\n"
            "- Do NOT invent fields.\n"
            "- Prefer fewer fields if the task can still be done.\n"
            "- If the user mentions dates, DO NOT build filters here; only include relevant date fields in the projection.\n\n"
            f"Allowed fields: {allowed_fields_sorted}\n\n"
            f"{few_shot}\n"
        ),
        (
            "human",
            "User query:\n{query}\n\n"
            "Respond in STRICT JSON using this schema:\n{format_instructions}"
        ),
    ]
)

def _generate_mongo_projection(query: str) -> Dict[str, Any]:
    """
    Use LLM to propose a minimal set of fields for the projection, then sanitize against a whitelist.
    Returns a dict that you can pass to MongoDB find(..., projection=...).
    """
    logger.info(f"[mongo_projection_tool] Building projection for query: {query}")

    try:
        chain = _prompt | llm | _parser
        parsed: ProjectionChoice = chain.invoke(
            {
                "query": query,
                "format_instructions": _parser.get_format_instructions(),
            }
        )

        print(type(parsed))

        if isinstance(parsed, ProjectionChoice):
            result = parsed
        elif isinstance(parsed, dict):
            result = ProjectionChoice.parse_obj(parsed)

        # Sanitize against whitelist
        seen = set()
        sanitized: List[str] = []
        for f in result.fields:
            if f in FIELD_WHITELIST and f not in seen:
                seen.add(f)
                sanitized.append(f)

        # Ensure minimal defaults
        for f in DEFAULT_INCLUDE:
            if f in FIELD_WHITELIST and f not in seen:
                seen.add(f)
                sanitized.append(f)
        
        if not sanitized:
            sanitized = list(DEFAULT_INCLUDE)

        projection: Dict[str, int] = {f: 1 for f in sanitized}
        if EXCLUDE_ID_BY_DEFAULT and "_id" not in sanitized:
            projection["_id"] = 0
        
        return {
            "projection": projection,
            "selected_fields": sanitized,
            "reasoning": result.reasoning,
            "parsed_successfully": True,
        }
    
    except Exception as e:
        logger.error(f"[mongo_projection_tool] Parsing failed: {e}")
        # Safe fallback
        fallback_fields = list(DEFAULT_INCLUDE)
        projection = {f: 1 for f in fallback_fields}
        if EXCLUDE_ID_BY_DEFAULT:
            projection["_id"] = 0

        return {
            "projection": projection,
            "selected_fields": fallback_fields,
            "reasoning": "Fallback to safe minimal defaults due to parse/validation error.",
            "parsed_successfully": False,
            "error": str(e),
        }

    

def get_mongo_projection_tool() -> StructuredTool:
    """
    Returns a sanitized MongoDB projection dict based on the user's query.

    NOTE: This tool does *not* build filters. It only returns a projection to
    minimize fetched fields. Use another tool in your pipeline to build filters
    (e.g., date ranges) and to actually query Mongo.
    """

    return StructuredTool.from_function(
        name="mongo_projection_tool",
        description=(
            "Generates a minimal MongoDB projection for the 'transactions' collection "
            "based on a natural-language user request. It returns only the fields "
            "necessary to answer the query, intersected with a safe whitelist. "
            "Use this to reduce payload size before a downstream LLM summarization tool."
        ),
        func=_generate_mongo_projection,
        args_schema=ProjectionToolInput,
        return_direct=False,
    )    