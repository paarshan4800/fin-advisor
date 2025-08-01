from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DateRangeExtractor(BaseModel):
    """Tool for extracting date ranges from natural language"""
    
    name: str = "date_range_extractor"
    description: str = "Extracts start and end dates from natural language queries"
    
    def _run(self, query: str) -> Dict[str, Any]:
        """Extract date range from query using LLM"""
        logger.info(f"Extracting date range from: {query}")
        
        # This would typically use an LLM to parse dates
        # For demo purposes, implementing basic logic
        current_date = datetime.now()
        
        if "last week" in query.lower():
            end_date = current_date - timedelta(days=current_date.weekday())
            start_date = end_date - timedelta(days=7)
        elif "last month" in query.lower():
            if current_date.month == 1:
                start_date = datetime(current_date.year - 1, 12, 1)
                end_date = datetime(current_date.year, 1, 1) - timedelta(days=1)
            else:
                start_date = datetime(current_date.year, current_date.month - 1, 1)
                end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
        elif "last two months" in query.lower():
            if current_date.month <= 2:
                start_date = datetime(current_date.year - 1, current_date.month + 10, 1)
            else:
                start_date = datetime(current_date.year, current_date.month - 2, 1)
            end_date = current_date
        else:
            # Default to last 30 days
            start_date = current_date - timedelta(days=30)
            end_date = current_date
        
        result = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "parsed_successfully": True
        }
        
        logger.info(f"Extracted date range: {result}")
        return result

def get_date_range_tool() -> Tool:
    """Create date range extraction tool"""
    extractor = DateRangeExtractor()
    
    return Tool(
        name=extractor.name,
        description=extractor.description,
        func=extractor._run
    )