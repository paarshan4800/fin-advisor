from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Iterable, List, Union
from datetime import datetime
from utils.logger import setup_logger
from agents.llm import llm
import json
from utils.constants import merchant_categories

logger = setup_logger(__name__)

CATEGORY_ENUM = list(merchant_categories.keys())
TYPE_ENUM = sorted({t for types in merchant_categories.values() for t in types})
TYPE_TO_CATEGORY = {t: cat for cat, types in merchant_categories.items() for t in types}

_category_norm = {c.lower(): c for c in CATEGORY_ENUM}
_type_norm = {t.lower(): t for t in TYPE_ENUM}

class QueryFilterInput(BaseModel):
    query: str = Field(..., description="The user's natural language question to extract filters from")

def to_iso(date_str: Optional[str]) -> Optional[str]:
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.isoformat(timespec="microseconds")
    return None

def _ensure_list(value: Optional[Union[str, Iterable[str]]]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return [v for v in value if isinstance(v, str)]
    except TypeError:
        return []

def _normalize_many(values: Iterable[str], norm_map: Dict[str, str]) -> List[str]:
    seen = set()
    out = []
    for v in values:
        key = v.strip().lower()
        if not key:
            continue
        norm = norm_map.get(key)
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out

def _extract_filters(query: str) -> Dict[str, Any]:

    logger.info(f"Extracting structured filters from query: {query}")

    today = datetime.now().strftime("%Y-%m-%d")
    category_union = " | ".join(f'"{c}"' for c in CATEGORY_ENUM)
    type_union = " | ".join(f'"{t}"' for t in TYPE_ENUM)

    prompt = (
        f"Today is {today}.\n"
        f"From the following user query, extract as many filters as possible and respond ONLY in this JSON format:\n"
        "{\n"
        '  "start_date": "YYYY-MM-DD",\n'
        '  "end_date": "YYYY-MM-DD",\n'
        '  "transaction_mode": ["Card" | "UPI" | "BankTransfer" | "Cash", ...] | [],\n'
        '  "currency": "INR" | "USD" | "EUR" | null,\n'
        '  "amount_min": number | null,\n'
        '  "amount_max": number | null,\n'
        '  "status": "initiated" | "success" | "failed" | "refunded" | null,\n'
        f'  "merchant_category": [{category_union}, ...] | [],\n'
        f'  "merchant_type": [{type_union}, ...] | []\n',
        '  "counterparty_name": string | null\n'
        "}\n\n"
        "Rules:\n"
        "- If the query mentions a person's name like 'John Doe', set counterparty_name to that name.\n"
        "- Only use merchant_category values from the provided list of categories.\n"
        "- Only use merchant_type values from the provided list of types.\n"
        "- If merchant_type has values, also include their parent category(ies) in merchant_category.\n"
        "- If a value is not mentioned in the query, set arrays to [] and scalars to null.\n\n"
        f"Query: '{query}'"
    )

    try:
        response = llm.invoke(prompt)
        logger.info(f"LLM raw response: {response.content}")

        result = json.loads(response.content)

        # Normalize dates
        result["start_date"] = to_iso(result.get("start_date"))
        result["end_date"] = to_iso(result.get("end_date"))

        raw_mc = _ensure_list(result.get("merchant_category"))
        raw_mt = _ensure_list(result.get("merchant_type"))
        raw_modes = _ensure_list(result.get("transaction_mode"))

        mc = _normalize_many(raw_mc, _category_norm)
        mt = _normalize_many(raw_mt, _type_norm)

        # If types present, add their parent categories to merchant_category
        implied_categories = []
        for t in mt:
            parent = TYPE_TO_CATEGORY.get(t)
            if parent:
                implied_categories.append(parent)
        implied_categories = _normalize_many(implied_categories, _category_norm)

        combined_mc = mc + [c for c in implied_categories if c not in mc]

        # Normalize transaction modes
        MODE_ENUM = {"Card", "UPI", "BankTransfer", "Cash"}
        modes = []
        for m in raw_modes:
            m_clean = m.strip()
            alias = {
                "bank transfer": "BankTransfer",
                "banktransfer": "BankTransfer",
                "debit": "Card",
                "credit": "Card",
            }.get(m_clean.lower(), m_clean)
            if alias in MODE_ENUM and alias not in modes:
                modes.append(alias)

        result["merchant_category"] = combined_mc
        result["merchant_type"] = mt
        result["transaction_mode"] = modes

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
            "transaction_mode": [],
            "currency": None,
            "amount_min": None,
            "amount_max": None,
            "status": None,
            "merchant_category": [],
            "merchant_type": [],
            "counterparty_name": None
        }

def get_query_filter_extractor_tool() -> StructuredTool:
    
    return StructuredTool.from_function(
        name="query_filter_extractor",
        description=(
            "Extracts structured filters from user query including: start_date, end_date, "
            "transaction_mode[], currency, amount_min, amount_max, status, merchant_category[], merchant_type[] and counterparty_name. "
            "Dates must be YYYY-MM-DD. Merchant fields are restricted to known categories/types and "
            "types automatically imply their parent categories. Returns JSON."
        ),
        func=_extract_filters,
        args_schema=QueryFilterInput,
        return_direct=False,
    )
