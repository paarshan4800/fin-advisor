import json, re
from typing import Any, Dict
from utils.logger import setup_logger

from agents.llm import llm_json

logger = setup_logger(__name__)

FALLBACK_ERROR_JSON = {
    "type": "table",
    "chartType": None,
    "text_summary": "Sorry, I couldn't parse the model output as JSON.",
    "data": [],
    "error": True
}

def _extract_json_local(text: str) -> Dict[str, Any]:
    s = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1).strip()
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1:
        s = s[start:end+1]
    return json.loads(s)

def _finalize_json(draft_text: str) -> Dict[str, Any]:
    """
    Use llm_json (JSON mode) when available; otherwise fallback to local parsing.
    """
    if llm_json is None:
        # Non-OpenAI path (e.g., Ollama)
        try:
            return _extract_json_local(draft_text)
        except Exception as e:
            logger.error(f"Local JSON parse failed: {e}; raw: {draft_text!r}")
            return FALLBACK_ERROR_JSON

    # OpenAI JSON-mode path
    # NOTE: At least one message must contain the word "json"
    sys = (
        "You are a formatter. Output ONLY a valid JSON object (no code fences, no backticks). "
        "Ensure keys and types exactly match the schema. If content is missing, use sensible defaults."
    )
    user = f"""
    Return a JSON object following this schema (respond ONLY with JSON):

    {{
    "type": "table" | "chart",
    "chartType": "bar" | "line" | "pie" | "scatter" | null,
    "text_summary": string,
    "data": any
    }}

    Here is the model's draft output (may include markdown fences). Convert it to clean JSON:

    === DRAFT START ===
    {draft_text}
    === DRAFT END ===
    """

    msg = [{"role": "system", "content": sys},
           {"role": "user", "content": user}]  # contains the word 'JSON/json'

    resp = llm_json.invoke(msg)
    try:
        return json.loads(resp.content)
    except Exception as e:
        logger.error(f"JSON-mode load failed: {e}; raw: {resp.content!r}")
        # last-ditch attempt
        try:
            return _extract_json_local(resp.content)
        except Exception as e2:
            logger.error(f"Final local parse failed: {e2}; raw: {resp.content!r}")
            return FALLBACK_ERROR_JSON
