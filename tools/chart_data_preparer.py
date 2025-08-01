from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ChartDataPreparer(BaseModel):
    """Tool for preparing data for different chart types"""
    
    name: str = "chart_data_preparer"
    description: str = "Prepares data in formats suitable for various chart types"
    
    def _run(self, raw_data: str) -> Dict[str, Any]:
        """Prepare chart data from raw query results"""
        logger.info("Preparing chart data")
        
        # This would process the actual query results
        # For demo, returning sample formatted data
        
        chart_formats = {
            "pie": {
                "data": [
                    {"label": "Food & Dining", "value": 15000, "color": "#FF6384"},
                    {"label": "Transportation", "value": 8000, "color": "#36A2EB"},
                    {"label": "Shopping", "value": 12000, "color": "#FFCE56"},
                    {"label": "Utilities", "value": 5000, "color": "#4BC0C0"}
                ]
            },
            "bar": {
                "data": [
                    {"category": "Food & Dining", "amount": 15000},
                    {"category": "Transportation", "amount": 8000},
                    {"category": "Shopping", "amount": 12000},
                    {"category": "Utilities", "amount": 5000}
                ]
            },
            "line": {
                "data": [
                    {"date": "2024-01-01", "amount": 5000},
                    {"date": "2024-01-02", "amount": 7000},
                    {"date": "2024-01-03", "amount": 4500},
                    {"date": "2024-01-04", "amount": 8000}
                ]
            },
            "table": {
                "headers": ["Date", "Description", "Category", "Amount"],
                "rows": [
                    ["2024-01-01", "Restaurant expense", "Food & Dining", 2500],
                    ["2024-01-02", "Uber ride", "Transportation", 450],
                    ["2024-01-03", "Grocery shopping", "Food & Dining", 3200]
                ]
            }
        }
        
        return chart_formats

def get_chart_data_preparer_tool() -> Tool:
    """Create chart data preparation tool"""
    preparer = ChartDataPreparer()
    
    return Tool(
        name=preparer.name,
        description=preparer.description,
        func=preparer._run
    )