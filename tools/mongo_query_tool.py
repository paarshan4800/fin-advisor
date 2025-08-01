from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from db.connection import mongo_conn
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MongoQueryTool(BaseModel):
    """Tool for querying MongoDB collections"""
    
    name: str = "mongo_query_tool"
    description: str = "Executes MongoDB queries and aggregations on financial data"
    
    def _run(self, query_params: str) -> Dict[str, Any]:
        """Execute MongoDB query based on parameters"""
        logger.info(f"Executing MongoDB query with params: {query_params}")
        
        try:
            db = mongo_conn.connect()
            
            # Parse query parameters (in real implementation, use LLM to parse)
            # For demo, implementing common query patterns
            
            if "spending by category" in query_params.lower():
                return self._get_spending_by_category(db, query_params)
            elif "transactions to" in query_params.lower():
                return self._get_transactions_to_person(db, query_params)
            elif "total spending" in query_params.lower():
                return self._get_total_spending(db, query_params)
            else:
                return self._get_recent_transactions(db, query_params)
                
        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            return {"error": str(e), "data": []}
    
    def _get_spending_by_category(self, db, query_params: str) -> Dict[str, Any]:
        """Get spending aggregated by category"""
        pipeline = [
            {
                "$match": {
                    "transaction_type": "debit",
                    "status": {"$in": ["completed", "success"]}
                }
            },
            {
                "$lookup": {
                    "from": "merchants",
                    "localField": "merchant_id",
                    "foreignField": "_id",
                    "as": "merchant"
                }
            },
            {
                "$unwind": "$merchant"
            },
            {
                "$group": {
                    "_id": "$merchant.category",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"total_amount": -1}
            }
        ]
        
        results = list(db.transactions.aggregate(pipeline))
        
        return {
            "query_type": "spending_by_category",
            "data": results,
            "total_categories": len(results)
        }
    
    def _get_transactions_to_person(self, db, query_params: str) -> Dict[str, Any]:
        """Get transactions to a specific person/merchant"""
        # Extract person name using simple string matching
        # In real implementation, use LLM for entity extraction
        person_name = "John"  # Default for demo
        
        pipeline = [
            {
                "$lookup": {
                    "from": "merchants",
                    "localField": "merchant_id",
                    "foreignField": "_id", 
                    "as": "merchant"
                }
            },
            {
                "$unwind": "$merchant"
            },
            {
                "$match": {
                    "merchant.name": {"$regex": person_name, "$options": "i"}
                }
            },
            {
                "$sort": {"initiated_at": -1}
            }
        ]
        
        results = list(db.transactions.aggregate(pipeline))
        total_amount = sum(t.get("amount", 0) for t in results)
        
        return {
            "query_type": "transactions_to_person",
            "person": person_name,
            "data": results,
            "total_amount": total_amount,
            "transaction_count": len(results)
        }
    
    def _get_total_spending(self, db, query_params: str) -> Dict[str, Any]:
        """Get total spending for a period"""
        pipeline = [
            {
                "$match": {
                    "transaction_type": "debit",
                    "status": {"$in": ["completed", "success"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            }
        ]
        
        results = list(db.transactions.aggregate(pipeline))
        
        return {
            "query_type": "total_spending",
            "data": results,
            "total_amount": results[0]["total_amount"] if results else 0
        }
    
    def _get_recent_transactions(self, db, query_params: str) -> Dict[str, Any]:
        """Get recent transactions"""
        pipeline = [
            {
                "$lookup": {
                    "from": "merchants",
                    "localField": "merchant_id",
                    "foreignField": "_id",
                    "as": "merchant"
                }
            },
            {
                "$unwind": "$merchant"
            },
            {
                "$sort": {"initiated_at": -1}
            },
            {
                "$limit": 20
            }
        ]
        
        results = list(db.transactions.aggregate(pipeline))
        
        return {
            "query_type": "recent_transactions",
            "data": results,
            "transaction_count": len(results)
        }

def get_mongo_query_tool() -> Tool:
    """Create MongoDB query tool"""
    query_tool = MongoQueryTool()
    
    return Tool(
        name=query_tool.name,
        description=query_tool.description,
        func=query_tool._run
    )