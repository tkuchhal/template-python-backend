import redis
import dotenv
from loguru import logger
from urllib.parse import urlparse

dotenv.load_dotenv()


class RedisAdapter:
    _instance = None
    _redis_url = None

    def __new__(cls, redis_url):
        if cls._instance is None:
            cls._instance = super(RedisAdapter, cls).__new__(cls)
            cls._instance._connection = None
            cls._redis_url = redis_url
        return cls._instance

    @property
    def connection(self):
        if self._connection is None:
            if self._redis_url is None:
                raise ValueError("REDIS_URL environment variable not set")

            url = urlparse(self._redis_url)
            self._connection = redis.Redis(
                connection_pool=redis.ConnectionPool(
                    host=url.hostname,
                    port=url.port,
                    db=0,
                    password=url.password,
                    max_connections=10  # You can adjust the max connections as needed
                )
            )

        return self._connection

    async def ping(self) -> (bool, str):
        try:
            return self.connection.ping(), 'ok'
        except redis.RedisError as e:
            logger.error(f"Failed to ping Redis: {e}")
            return False, e

    def get(self, key):
        try:
            value = self.connection.get(key)
            if value is not None:
                value = value.decode('utf-8')
            return value
        except redis.RedisError as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    def set(self, key, value, expire=None):
        try:
            self.connection.set(key, value, ex=expire)
        except redis.RedisError as e:
            logger.error(f"Failed to set key {key}: {e}")

    def delete(self, key):
        try:
            self.connection.delete(key)
        except redis.RedisError as e:
            logger.error(f"Failed to delete key {key}: {e}")

    def get_url(self):
        return self._redis_url
