from db.connection import mongo_conn
from utils.logger import setup_logger
from datetime import datetime
from pymongo import DESCENDING
from utils.mongo_utils import serialize

logger = setup_logger(__name__)

def build_query(user_id: str, criteria: dict):

    from_date = criteria.get("fromDate")
    to_date = criteria.get("toDate")
    status = criteria.get("status")
    transaction_mode = criteria.get("transactionMode")
    transaction_type = criteria.get("transactionType")

    query = {"user_id": user_id}

    if from_date or to_date:
        query["initiated_at"] = {}
        if from_date:
            query["initiated_at"]["$gte"] = datetime.fromisoformat(from_date)
        if to_date:
            query["initiated_at"]["$lte"] = datetime.fromisoformat(to_date)

    if status:
        query["status"] = status
    if transaction_mode:
        query["transaction_mode"] = transaction_mode
    if transaction_type:
        query["transaction_type"] = transaction_type

    return query


def get_transactions(user_id: str, criteria: dict):
    try:
        page_size = int(criteria.get("pageSize", 25))
        page_number = int(criteria.get("pageNumber", 1))
        skip_count = max(page_number - 1, 0) * page_size

        # Build query from filter criteria
        base_query = build_query(user_id, criteria)

        db = mongo_conn.connect()
        tx = db.transactions

        pipeline = [
            {"$match": base_query},
            {
                "$facet": {
                    "items": [
                        {"$sort": {"initiated_at": DESCENDING}},
                        {"$skip": skip_count},
                        {"$limit": page_size},
                        {
                            "$project": {
                                "_id": 1,
                                "transaction_id": 1,
                                "user_id": 1,
                                "from_account": {
                                    "_id": 1,
                                    "user_id": 1,
                                    "user_name": 1,
                                    "account_number": 1,
                                },
                                "to_account": 1,
                                "merchant": {
                                    "_id": 1,
                                    "name": 1,
                                    "type": 1,
                                    "category": 1,
                                },
                                "amount": 1,
                                "currency": 1,
                                "transaction_type": 1,
                                "transaction_mode": 1,
                                "status": 1,
                                "initiated_at": 1,
                                "completed_at": 1,
                                "failed_at": 1,
                                "remarks": 1,
                                "description": 1,
                                "reference_number": 1,
                                "order_id": 1,
                                "created_at": 1,
                                "updated_at": 1,
                            }
                        },
                    ],
                    "count": [
                        {"$count": "total_records"}
                    ],
                }
            },
            {
                "$project": {
                    "items": 1,
                    "total_records": {
                        "$ifNull": [{"$arrayElemAt": ["$count.total_records", 0]}, 0]
                    },
                }
            },
        ]

        agg = list(tx.aggregate(pipeline, allowDiskUse=True))
        if not agg:
            return {
                "items": [],
                "total_records": 0,
                "page_number": page_number,
                "page_size": page_size,
                "total_pages": 0,
            }

        items = agg[0].get("items", [])
        total_records = int(agg[0].get("total_records", 0))

        items = [serialize(doc) for doc in items]

        return {
            "items": items,
            "total_records": total_records,
            "page_number": page_number,
            "page_size": page_size,
            "total_pages": (total_records + page_size - 1) // page_size,
        }

    except Exception as e:
        logger.exception(f"MongoDB aggregation failed: {e}")
        return {"error": str(e)}
