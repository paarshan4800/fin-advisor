from db.connection import mongo_conn
from utils.logger import setup_logger
from pymongo import DESCENDING
from bson import ObjectId, Decimal128
from datetime import datetime

logger = setup_logger(__name__)

def serialize(doc):
    """Convert Mongo types to JSON-safe values."""
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, Decimal128):
        return float(doc.to_decimal())
    if isinstance(doc, datetime):
        return doc.isoformat()
    if isinstance(doc, dict):
        return {k: serialize(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [serialize(v) for v in doc]
    return doc

def get_transactions(user_id: str, page_size: int, page_number: int):
    try:
        
        db = mongo_conn.connect()
        collection = db.transactions

        total_records = collection.count_documents({"user_id": user_id})

        skip_count = (page_number - 1) * page_size

        cursor = (
            collection.find({"user_id": user_id})
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