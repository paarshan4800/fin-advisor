from flask import Flask, jsonify, request
from flask_cors import CORS
from config.settings import settings
from routes.transactions import transactions_bp
from routes.insights import insights_bp
from routes.users import users_bp
from db.connection import mongo_conn
from utils.logger import setup_logger
from utils.context import current_user_id
import atexit

logger = setup_logger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": {
                "message": "Endpoint not found",
                "details": "The requested resource was not found on this server"
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "error": {
                "message": "Internal server error",
                "details": "An unexpected error occurred"
            }
        }), 500
    
    @app.before_request
    def attach_user_id():
        if request.method == "OPTIONS":
            return ("", 204)
        
        if request.method == "POST":
            payload = request.json or {}
            uid = payload.get("userId") or payload.get("session_id")
            current_user_id.set(uid)

    @app.teardown_request
    def clear_user_id(exc):
        current_user_id.set(None)
    
    # Initialize database connection
    try:
        mongo_conn.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    # Register cleanup handler
    atexit.register(mongo_conn.close)
    
    return app

if __name__ == '__main__':
    
    app = create_app()
    logger.info(f"Starting Finance AI Assistant on port {settings.FLASK_PORT}")
    logger.info(f"Debug mode: {settings.FLASK_DEBUG}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    app.run(
        host='0.0.0.0',
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG
    )