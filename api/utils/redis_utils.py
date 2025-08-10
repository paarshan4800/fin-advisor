import redis
from config.settings import settings

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host= settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.default_ttl = int(settings.REDIS_TTL)
        self.namespace = settings.REDIS_NAMESPACE 

    def _namespaced_key(self, key: str) -> str:
        """Apply namespace prefix to a key."""
        return f"{self.namespace}:{key}"

    def set_data(self, key: str, value, ttl: int = None):
        """Set a value in Redis with optional TTL."""
        namespaced_key = self._namespaced_key(key)
        ttl = ttl or self.default_ttl
        self.redis.setex(namespaced_key, ttl, value)

    def get_data(self, key: str):
        """Retrieve a value from Redis."""
        namespaced_key = self._namespaced_key(key)
        return self.redis.get(namespaced_key)

    def delete_data(self, key: str):
        """Delete a key from Redis."""
        namespaced_key = self._namespaced_key(key)
        self.redis.delete(namespaced_key)

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        namespaced_key = self._namespaced_key(key)
        return self.redis.exists(namespaced_key) > 0

# Singleton instance
redis_client = RedisClient()
