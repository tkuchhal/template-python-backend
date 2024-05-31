# app/celery_config.py
import pytest
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer
from testcontainers.mongodb import MongoDbContainer
from pymongo import MongoClient
from testcontainers.postgres import PostgresContainer
import os
import time


@pytest.fixture(scope='session')
def postgres_container() -> PostgresContainer:
    container = PostgresContainer("postgres:latest", dbname='test')
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope='session')
def redis_container() -> RedisContainer:
    container = RedisContainer("redis:latest").with_exposed_ports(6379)
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope='session')
def mongodb_container() -> MongoDbContainer:
    container = MongoDbContainer("mongo:latest").with_exposed_ports(27017)
    container.start()

    # Wait for MongoDB to become ready
    connection_url = container.get_connection_url()
    client = MongoClient(connection_url)
    timeout = 10  # seconds
    start_time = time.time()

    while True:
        try:
            # The ismaster command is fast and does not require auth.
            client.admin.command('ismaster')
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"MongoDB container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    yield container
    container.stop()


@pytest.fixture(scope='session')
def api_client(postgres_container: PostgresContainer,
               mongodb_container: MongoDbContainer,
               redis_container: RedisContainer) -> TestClient:
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['REDIS_URL'] = f'redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}'
    os.environ['MONGO_URL'] = f'{mongodb_container.get_connection_url()}'
    from app.main import app
    client = TestClient(app)
    yield client


@pytest.fixture(scope='session')
def celery(postgres_container: PostgresContainer,
           mongodb_container: MongoDbContainer,
           redis_container: RedisContainer):
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['REDIS_URL'] = f'redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}'
    os.environ['MONGO_URL'] = f'{mongodb_container.get_connection_url()}'
    from app.tasks.celery_config import celery
    celery.conf.update(
        task_always_eager=True,
        broker_url=os.getenv('REDIS_URL'),
        result_backend=os.getenv('REDIS_URL'),
    )
    yield celery
