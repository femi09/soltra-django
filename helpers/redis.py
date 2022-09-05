import redis
from django.conf import settings

class RedisUtility:
    def __init__(self) -> None:
        self.redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    
    def set_value(self, key, value, expire):
        return self.redis_instance.set(key, value, ex=expire)
    
    def get_value(self, key):
        return self.redis_instance.get(key)
    
    def delete_value(self, key):
        return self.redis_instance.delete(key)
    
redis_utils = RedisUtility()