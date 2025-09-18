from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from urllib.parse import urlparse
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MongoConnection:
    _instance = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Database:
        if self._db is None:
            try:
                self._client = MongoClient(settings.MONGO_URI)

                # Extract database name
                parsed = urlparse(settings.MONGO_URI)
                db_name = parsed.path.lstrip("/") or "default"

                self._db = self._client[db_name]
                logger.info(f"Connected to MongoDB database: {db_name}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return self._db

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")


mongo_conn = MongoConnection()
