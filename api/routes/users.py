from flask import Blueprint, request, jsonify
from typing import Dict, Any
from utils.response_formatter import ResponseFormatter
from utils.logger import setup_logger
from services.users import get_all_users

logger = setup_logger(__name__)

users_bp = Blueprint('users', __name__)

@users_bp.route('/all', methods=['GET'])
def transactions() -> Dict[str, Any]:
    try:                           
        logger.info(f"Received request for get all users")
        
        result = get_all_users()
        
        return jsonify(ResponseFormatter.success_response(result))
        
    except Exception as e:
        logger.error(f"Unexpected error in /users/all endpoint: {e}")
        return jsonify(ResponseFormatter.error_response(
            "Internal server error",
            str(e)
        )), 500
