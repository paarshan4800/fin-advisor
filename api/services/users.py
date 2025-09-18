from db.connection import mongo_conn
from utils.logger import setup_logger
from bson import ObjectId, Decimal128
from datetime import datetime
from utils.mongo_utils import serialize

logger = setup_logger(__name__)

def get_all_users():
    try:
        db = mongo_conn.connect()
        collection = db.users

        cursor = collection.find({})
        results = [serialize(doc) for doc in cursor]

        return {"items": results, "total_records": len(results)}

    except Exception as e:
        logger.error(f"MongoDB query failed: {e}")
        return {"error": str(e)}
