from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CategoryMapper(BaseModel):
    """Tool for mapping and analyzing spending categories"""
    
    name: str = "category_mapper"
    description: str = "Maps transactions to spending categories and identifies patterns"
    
    def _run(self, transaction_data: str) -> Dict[str, Any]:
        """Analyze and map transaction categories"""
        logger.info("Mapping transaction categories")
        
        # In real implementation, this would use LLM to categorize
        # For demo, using predefined category mapping
        
        category_suggestions = {
            "Food & Dining": ["restaurant", "food", "cafe", "dining"],
            "Transportation": ["uber", "taxi", "gas", "fuel", "transport"],
            "Shopping": ["store", "shop", "retail", "amazon"],
            "Utilities": ["electric", "water", "internet", "phone", "mobile"],
            "Entertainment": ["movie", "game", "streaming", "music"],
            "Healthcare": ["hospital", "doctor", "pharmacy", "medical"],
            "Education": ["course", "book", "school", "university"]
        }
        
        unnecessary_spending_patterns = [
            "Multiple transactions to same restaurant in a day",
            "High-frequency small purchases",
            "Subscriptions for unused services",
            "Impulse shopping patterns"
        ]
        
        return {
            "category_mapping": category_suggestions,
            "unnecessary_patterns": unnecessary_spending_patterns,
            "recommendations": [
                "Set daily spending limits for dining",
                "Review and cancel unused subscriptions",
                "Use budgeting apps for impulse control"
            ]
        }

def get_category_mapper_tool() -> Tool:
    """Create category mapping tool"""
    mapper = CategoryMapper()
    
    return Tool(
        name=mapper.name,
        description=mapper.description,
        func=mapper._run
    )