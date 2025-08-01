from flask import Blueprint, request, jsonify
from typing import Dict, Any
from agents.finance_agent import finance_agent
from utils.response_formatter import ResponseFormatter
from utils.logger import setup_logger

logger = setup_logger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/query', methods=['POST'])
def process_financial_query() -> Dict[str, Any]:
    """Process financial query endpoint"""
    try:
        # Validate request
        if not request.json:
            return jsonify(ResponseFormatter.error_response(
                "Request body must be JSON"
            )), 400
        
        user_query = request.json.get('query', '').strip()
        session_id = request.json.get('session_id', 'default')
        
        if not user_query:
            return jsonify(ResponseFormatter.error_response(
                "Query parameter is required"
            )), 400
        
        logger.info(f"Received query: '{user_query}' for session: {session_id}")
        
        # Process query with AI agent
        result = finance_agent.process_query(user_query, session_id)
        
        # Validate response structure
        if not ResponseFormatter.validate_query_response(result):
            logger.error(f"Invalid response structure: {result}")
            return jsonify(ResponseFormatter.error_response(
                "Internal processing error - invalid response format"
            )), 500
        
        return jsonify(ResponseFormatter.success_response(result))
        
    except Exception as e:
        logger.error(f"Unexpected error in /query endpoint: {e}")
        return jsonify(ResponseFormatter.error_response(
            "Internal server error",
            str(e)
        )), 500

@api_bp.route('/health', methods=['GET'])
def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "finance-ai-assistant",
        "version": "1.0.0"
    })

@api_bp.route('/memory/<session_id>', methods=['GET'])
def get_conversation_history(session_id: str) -> Dict[str, Any]:
    """Get conversation history for a session"""
    try:
        from agents.memory import conversation_memory
        
        context = conversation_memory.get_context(session_id)
        
        if not context:
            return jsonify(ResponseFormatter.success_response({
                "session_id": session_id,
                "history": [],
                "message": "No conversation history found"
            }))
        
        return jsonify(ResponseFormatter.success_response({
            "session_id": session_id,
            "history": conversation_memory.conversations.get(session_id, [])
        }))
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        return jsonify(ResponseFormatter.error_response(
            "Failed to retrieve conversation history",
            str(e)
        )), 500

@api_bp.route('/memory/<session_id>', methods=['DELETE'])
def clear_conversation_history(session_id: str) -> Dict[str, Any]:
    """Clear conversation history for a session"""
    try:
        from agents.memory import conversation_memory
        
        if session_id in conversation_memory.conversations:
            del conversation_memory.conversations[session_id]
            logger.info(f"Cleared conversation history for session: {session_id}")
        
        return jsonify(ResponseFormatter.success_response({
            "message": f"Conversation history cleared for session: {session_id}"
        }))
        
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        return jsonify(ResponseFormatter.error_response(
            "Failed to clear conversation history",
            str(e)
        )), 500