from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ResponseFormatter:
    """Utility class for formatting API responses"""
    
    @staticmethod
    def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful response"""
        return {
            "success": True,
            "data": data,
            "error": None
        }
    
    @staticmethod
    def error_response(message: str, details: str = None) -> Dict[str, Any]:
        """Format error response"""
        logger.error(f"API Error: {message}")
        return {
            "success": False,
            "data": None,
            "error": {
                "message": message,
                "details": details
            }
        }
    
    @staticmethod
    def validate_query_response(response: Dict[str, Any]) -> bool:
        """Validate query response structure"""
        required_fields = ["type", "text_summary", "data"]
        return all(field in response for field in required_fields)