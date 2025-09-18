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
        return f"{self.namespace}:{key}"

    def set_data(self, key: str, value, ttl: int = None):
        namespaced_key = self._namespaced_key(key)
        ttl = ttl or self.default_ttl
        self.redis.setex(namespaced_key, ttl, value)

    def get_data(self, key: str):
        namespaced_key = self._namespaced_key(key)
        return self.redis.get(namespaced_key)

    def exists(self, key: str) -> bool:
        namespaced_key = self._namespaced_key(key)
        return self.redis.exists(namespaced_key) > 0

redis_client = RedisClient()
