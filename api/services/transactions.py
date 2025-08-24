from db.connection import mongo_conn
from utils.logger import setup_logger
from pymongo import DESCENDING
from bson import ObjectId, Decimal128
from datetime import datetime
from utils.mongo_utils import serialize

logger = setup_logger(__name__)

def build_query(user_id: str, criteria: dict):
    from_date = criteria.get("fromDate")
    to_date = criteria.get("toDate")
    status = criteria.get("status")
    transaction_mode = criteria.get("transactionMode")
    transaction_type = criteria.get("transactionType")

    query = {"user_id": user_id}

    # Handle date filters
    if from_date or to_date:
        query["initiated_at"] = {}
        if from_date:
            query["initiated_at"]["$gte"] = datetime.fromisoformat(from_date)
        if to_date:
            query["initiated_at"]["$lte"] = datetime.fromisoformat(to_date)

    # Handle status filter
    if status:
        query["status"] = status

    # Handle transaction mode filter
    if transaction_mode:
        query["transaction_mode"] = transaction_mode

    # Handle transaction type filter
    if transaction_type:
        query["transaction_type"] = transaction_type

    print("query", query)

    return query


def get_transactions(user_id: str, criteria: dict):
    try:
        
        page_size = criteria.get('pageSize', 25)
        page_number = criteria.get('pageNumber', 1)

        query = build_query(user_id, criteria)

        db = mongo_conn.connect()
        collection = db.transactions

        total_records = collection.count_documents(query)

        skip_count = (page_number - 1) * page_size

        cursor = (
            collection.find(query)
            .sort("initiated_at", DESCENDING)
            .skip(skip_count)
            .limit(page_size)
        )

        results = [serialize(doc) for doc in cursor]
        
        return {
            "items": results,
            "total_records": total_records,
            "page_number": page_number,
            "page_size": page_size,
            "total_pages": (total_records + page_size - 1) // page_size
        }

    except Exception as e:
        logger.error(f"MongoDB query failed: {e}")
        return {"error": str(e)}