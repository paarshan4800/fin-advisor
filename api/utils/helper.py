from typing import Dict, Any, List, Union, Optional
import hashlib, json
from utils.redis_utils import redis_client
from datetime import datetime, timezone
from bson import ObjectId, Decimal128

def _make_handle(query_filter: Dict[str, Any], projection: Dict[str, int], now_iso: str) -> str:
    # Stable hash of filter+projection+timestamp to avoid collisions but enable idempotency windows if needed
    m = hashlib.sha256()
    m.update(json.dumps(query_filter, sort_keys=True).encode("utf-8"))
    m.update(b"|")
    m.update(json.dumps(projection, sort_keys=True).encode("utf-8"))
    m.update(b"|")
    m.update(now_iso.encode("utf-8"))
    return "mq:" + m.hexdigest()[:24]

def _coerce_transactions(obj: Union[str, List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    if obj is None:
        return []
    if isinstance(obj, str):
        obj = json.loads(obj)
    if isinstance(obj, dict):
        # allow single object form
        return [obj]
    if isinstance(obj, list):
        return obj
    raise ValueError("transaction_data must be JSON string, list[dict], or dict")

def _load_data_from_handle(handle: str) -> List[Dict[str, Any]]:
    cached = redis_client.get_data(handle)
    if not cached:
        raise ValueError(f"Handle not found or expired: {handle}")
    payload = json.loads(cached)
    # We stored the full rows under "data" in mongo_query_tool
    return payload.get("data", [])


def _clean_for_json(doc: Dict[str, Any]) -> Dict[str, Any]:
    # Convert Mongo types to JSON-safe primitives
    out = {}
    for k, v in doc.items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, Decimal128):
            out[k] = float(v.to_decimal())
        elif isinstance(v, dict):
            out[k] = _clean_for_json(v)
        elif isinstance(v, list):
            out[k] = [_clean_for_json(x) if isinstance(x, dict) else x for x in v]
        else:
            out[k] = v
    return out

def steps_by_tool(intermediate_steps):
    """
    Returns {tool_name: {"input": last_tool_input, "output": last_tool_output}}
    If a tool is called multiple times, keeps the last one.
    """

    def _maybe_json(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                return x
        return x

    out = {}
    for step in intermediate_steps:
        if not (isinstance(step, tuple) and len(step) == 2):
            continue
        action, tool_output = step
        tool_name = getattr(action, "tool", None) or (action.get("tool") if isinstance(action, dict) else None)
        if not tool_name:
            continue
        tool_input = getattr(action, "tool_input", None)
        out[tool_name] = {
            "input": _maybe_json(tool_input),
            "output": tool_output
        }
    return out


def enhance_response(result):
    resp = {}

    tool_outputs = steps_by_tool(result["intermediate_steps"])

    def get_visualization(data):
        return data.get("output", {})
    
    def get_analysis(data):
        output = data.get("output", {})
        return {
            'unnecessary_patterns': output.get("unnecessary_patterns", []),
            'recommendations': output.get("recommendations", []),
        }

    resp['query'] = result["input"]
    resp['visualization'] = get_visualization(tool_outputs.get("chart_data_preparer", {}))
    resp['analysis'] = get_analysis(tool_outputs.get("category_mapper", {}))

    return resp