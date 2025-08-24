# users.py
from db.connection import mongo_conn
from utils.logger import setup_logger
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

def get_all_users():
    """Return all users from the users collection."""
    try:
        db = mongo_conn.connect()
        collection = db.users

        cursor = collection.find({})
        results = [serialize(doc) for doc in cursor]

        return {"items": results, "total_records": len(results)}

    except Exception as e:
        logger.error(f"MongoDB query failed: {e}")
        return {"error": str(e)}
