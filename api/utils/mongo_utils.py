from bson import ObjectId, Decimal128
from datetime import datetime

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