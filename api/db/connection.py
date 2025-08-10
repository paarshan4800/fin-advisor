from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MongoConnection:
    """MongoDB connection manager"""
    
    _instance: Optional['MongoConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls) -> 'MongoConnection':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self) -> Database:
        """Establish MongoDB connection"""
        if self._db is None:
            try:
                self._client = MongoClient(settings.MONGO_URI)
                # Extract database name from URI
                db_name = settings.MONGO_URI.split('/')[-1]
                self._db = self._client[db_name]
                logger.info(f"Connected to MongoDB database: {db_name}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return self._db
    
    def close(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

# Global connection instance
mongo_conn = MongoConnection()