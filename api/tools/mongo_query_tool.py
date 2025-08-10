# Tool
from langchain.tools import Tool
from pydantic import BaseModel
from typing import Dict, Any
from db.connection import mongo_conn
from utils.logger import setup_logger
import json, copy
from utils.redis_utils import redis_client
from config.settings import settings
from datetime import datetime, timezone
from utils.helper import _make_handle, _clean_for_json


logger = setup_logger(__name__)

class MongoQueryTool(BaseModel):
    """Tool for querying MongoDB transactions using structured filters"""

    name: str = "mongo_query_tool"
    description: str = (
        "Executes a MongoDB query based on a structured filter and returns a small summary plus a cache handle. "
        "Downstream tools should use the handle to page or re-use results. "
        "The input should be a valid MongoDB query object. "
        "For date filtering, use the 'initiated_at' field with $gte and $lt."
    )

    def _run(self, query_filter: Any) -> Dict[str, Any]:
        """Execute MongoDB query using provided filter"""
        logger.info(f"[mongo_query_tool]: Running MongoDB query with filter: {query_filter}")

        try:
            # Parse string input to dict if needed
            if isinstance(query_filter, str):
                query_filter = json.loads(query_filter)

            mongo_query_filter = copy.deepcopy(query_filter)

            # Convert ISO strings in `initiated_at` to actual datetime objects
            if "initiated_at" in mongo_query_filter:
                initiated = mongo_query_filter["initiated_at"]
                mongo_query_filter["initiated_at"] = {
                    k: datetime.fromisoformat(v)
                    for k, v in initiated.items()
                }

            db = mongo_conn.connect()
            collection = db.transactions

            projection = {
                "_id": 0,
                "transaction_id": 1,
                "merchant_id": 1,
                "amount": 1,
                "currency": 1,
                "transaction_type": 1,
                "transaction_mode": 1,
                "status": 1,
                "initiated_at": 1,
                "remarks": 1,
                "description": 1
            }

            # Run the dynamic query
            results = list(collection.find(mongo_query_filter, projection).sort("initiated_at", -1))

            total_amount = sum(t.get("amount", 0) for t in results)
            transaction_count = len(results)

            # Clean for JSON (avoid ObjectId/datetime issues)
            cleanedResult = [_clean_for_json(r) for r in results]

            logger.info(f"Fetched {transaction_count} transactions for the given filter")

            # Compute quick date span & sample
            if transaction_count:
                # initiated_at are ISO strings after cleaning
                dates = [datetime.fromisoformat(t["initiated_at"]) for t in cleanedResult if t.get("initiated_at")]
                min_date = min(dates).isoformat() if dates else None
                max_date = max(dates).isoformat() if dates else None
            else:
                min_date = max_date = None

            fields = list(projection.keys())
            fields = [f for f, inc in projection.items() if inc]  # clean include-only

            sample_n = 3 if transaction_count >= 3 else transaction_count
            sample = cleanedResult[:sample_n]

            now_iso = datetime.now(timezone.utc).isoformat()
            handle = _make_handle(query_filter, projection, now_iso)

            # Store full payload in Redis
            cache_payload = {
                "handle": handle,
                "created_at": now_iso,
                "ttl_seconds": settings.REDIS_TTL,
                "query_filter": query_filter,    # echo original (string dates)
                "projection": projection,
                "metrics": {
                    "transaction_count": transaction_count,
                    "total_amount": total_amount,
                    "date_min": min_date,
                    "date_max": max_date,
                },
                # Store full rows for paging / downstream processing
                "data": cleanedResult,
            }

            redis_client.set_data(handle, json.dumps(cache_payload))

            logger.info(f"[mongo_query_tool]: stored {transaction_count} rows under {handle}")

            # Return small, LLM-friendly summary
            return {
                "query_type": "dynamic_filter_query",
                "handle": handle,
                "summary": {
                    "transaction_count": transaction_count,
                    "total_amount": total_amount,
                    "date_min": min_date,
                    "date_max": max_date,
                    "fields": fields,
                    "sample": sample,
                },
                # Optional echo for traceability (small)
                "query_echo": {
                    "filter": query_filter,
                    "projection": projection,
                },
            }

        except Exception as e:
            logger.error(f"[mongo_query_tool]: MongoDB query failed: {e}")
            return {"error": str(e)}


def get_mongo_query_tool() -> Tool:
    """Create MongoDB query tool"""
    query_tool = MongoQueryTool()

    return Tool(
        name=query_tool.name,
        description=query_tool.description,
        func=query_tool._run
    )
