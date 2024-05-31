import os
from typing import Union
import dotenv

from app.adapters.mongodb.main import MongoDBAdapter
from app.adapters.postgres.main import PostgresAdapter
from app.adapters.redis.main import RedisAdapter
from app.models import main as models


class ConfigManager:
    _db_instance: Union[PostgresAdapter, None] = None
    _redis_instance: Union[RedisAdapter, None] = None
    _mongodb_instance: Union[MongoDBAdapter, None] = None
    _migrations_run: bool = False

    @staticmethod
    def initialize():
        if os.getenv('ENVIRONMENT') != 'test':
            # Used for unit test. We skip loading local .env so the test framework can inject the
            # environment variables without getting overridden
            dotenv.load_dotenv()

        db_configured: bool = os.getenv('DATABASE_URL') is not None
        redis_configured: bool = os.getenv('REDIS_URL') is not None
        mongodb_configured: bool = os.getenv('MONGO_URL') is not None

        if ConfigManager._db_instance is None and db_configured:
            ConfigManager._db_instance = PostgresAdapter(db_url=os.getenv('DATABASE_URL'))
        if ConfigManager._redis_instance is None and redis_configured:
            ConfigManager._redis_instance = RedisAdapter(redis_url=os.getenv('REDIS_URL'))
        if ConfigManager._mongodb_instance is None and mongodb_configured:
            ConfigManager._mongodb_instance = MongoDBAdapter(mongodb_url=os.getenv('MONGO_URL'))

        if not ConfigManager._migrations_run and db_configured and ConfigManager._db_instance.ping():
            ConfigManager._migrations_run = True
            models.run_migrations(db_instance=ConfigManager._db_instance)

    @classmethod
    def get_redis_adapter(cls) -> RedisAdapter:
        cls.initialize()
        return cls._redis_instance

    @classmethod
    def get_postgres_adapter(cls) -> PostgresAdapter:
        cls.initialize()
        return cls._db_instance

    @classmethod
    def get_mongodb_adapter(cls) -> MongoDBAdapter:
        cls.initialize()
        return cls._mongodb_instance
