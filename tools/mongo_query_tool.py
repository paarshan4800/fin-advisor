# Tool
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel
from typing import Dict, Any
from datetime import datetime
from db.connection import mongo_conn
from utils.logger import setup_logger
import json
from bson import json_util, ObjectId, Decimal128
import copy

logger = setup_logger(__name__)

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

class MongoQueryTool(BaseModel):
    """Tool for querying MongoDB transactions using structured filters"""

    name: str = "mongo_query_tool"
    description: str = (
        "Fetches transactions from MongoDB using structured filters. "
        "The input should be a valid MongoDB query object. "
        "For date filtering, use the 'initiated_at' field with $gte and $lt."
    )

    def _run(self, query_filter: Any) -> Dict[str, Any]:
        """Execute MongoDB query using provided filter"""
        logger.info(f"Running MongoDB query with filter: {query_filter}")

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
            results = list(collection.find(mongo_query_filter, projection).sort("initiated_at", -1).limit(10))

            total_amount = sum(t.get("amount", 0) for t in results)
            transaction_count = len(results)

            # Clean for JSON (avoid ObjectId/datetime issues)
            cleanedResult = [_clean_for_json(r) for r in results]

            logger.info(f"Fetched {transaction_count} transactions for the given filter")

            return {
                "query_type": "dynamic_filter_query",
                "query_filter": query_filter,
                "data": cleanedResult,
                "total_amount": total_amount,
                "transaction_count": transaction_count
            }

        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            return {"error": str(e), "data": [], "query_filter": query_filter}


def get_mongo_query_tool() -> Tool:
    """Create MongoDB query tool"""
    query_tool = MongoQueryTool()

    return Tool(
        name=query_tool.name,
        description=query_tool.description,
        func=query_tool._run
    )
