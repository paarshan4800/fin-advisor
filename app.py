from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import settings
from routes.api import api_bp
from db.connection import mongo_conn
from utils.logger import setup_logger
import atexit

logger = setup_logger(__name__)

def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
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
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            "service": "Personal Finance AI Assistant",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "query": "/api/query",
                "health": "/api/health",
                "memory": "/api/memory/<session_id>"
            }
        })
    
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
    # Validate settings
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    # Create and run app
    app = create_app()
    logger.info(f"Starting Finance AI Assistant on port {settings.FLASK_PORT}")
    logger.info(f"Debug mode: {settings.FLASK_DEBUG}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    app.run(
        host='0.0.0.0',
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG
    )