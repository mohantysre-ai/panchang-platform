import json
from .config import settings

class Cache:
    def __init__(self):
        self.redis = None
        self.local = {}
        if settings.redis_enabled:
            try:
                import redis
                client = redis.Redis.from_url(
                    settings.redis_url, decode_responses=True,
                    socket_connect_timeout=1, socket_timeout=1
                )
                client.ping()
                self.redis = client
            except Exception:
                self.redis = None

    def get(self, key):
        if self.redis:
            try:
                value = self.redis.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                pass
        return self.local.get(key)

    def set(self, key, value, ttl=None):
        self.local[key] = value
        if len(self.local) > 2048:
            self.local.pop(next(iter(self.local)))
        if self.redis:
            try:
                self.redis.setex(
                    key, ttl or settings.redis_ttl_seconds,
                    json.dumps(value, ensure_ascii=False)
                )
            except Exception:
                pass

    def status(self):
        return {"redis": bool(self.redis), "local_entries": len(self.local)}

cache = Cache()
