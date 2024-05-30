# app/main.py
import pytest
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer
from testcontainers.mongodb import MongoDbContainer
from testcontainers.postgres import PostgresContainer
import os


@pytest.fixture(scope='session')
def postgres_container() -> PostgresContainer:
    container = PostgresContainer("postgres:latest")
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
    container = MongoDbContainer("mongo:latest").with_exposed_ports(6379)
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope='session')
def api_client(postgres_container: PostgresContainer,
               mongodb_container: MongoDbContainer,
               redis_container: RedisContainer) -> TestClient:
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['REDIS_URL'] = f'redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0'
    os.environ['MONGO_URL'] = f'{mongodb_container.get_connection_url()}'
    from app.main import app
    client = TestClient(app)
    yield client
