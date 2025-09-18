from flask import Blueprint, request, jsonify
from typing import Dict, Any
from utils.response_formatter import ResponseFormatter
from utils.logger import setup_logger
from services.transactions import get_transactions

logger = setup_logger(__name__)

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/get', methods=['POST'])
def transactions() -> Dict[str, Any]:
    try:
        # Validate request
        if not request.json:
            return jsonify(ResponseFormatter.error_response(
                "Request body must be JSON"
            )), 400
        
        user_id = request.json.get('userId', 'default')
        
        if not user_id:
            return jsonify(ResponseFormatter.error_response(
                "User ID is required"
            )), 400
        
        payload = request.get_json(silent=True, force=True) or {}
        
        logger.info(f"Received request for transactions for session: {user_id}")
        
        result = get_transactions(user_id, payload)
        
        return jsonify(ResponseFormatter.success_response(result))
        
    except Exception as e:
        logger.error(f"Unexpected error in /transactions endpoint: {e}")
        return jsonify(ResponseFormatter.error_response(
            "Internal server error",
            str(e)
        )), 500
