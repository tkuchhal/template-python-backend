# app/celery_config.py
import pytest
import requests
from fastapi.testclient import TestClient
from testcontainers.core.container import DockerContainer
import os
from tests import wiremock
import time
from pymongo import MongoClient


@pytest.fixture(scope='session')
def postgres_container() -> DockerContainer:
    container = DockerContainer("postgres:latest")
    container.with_env("POSTGRES_USER", "test")
    container.with_env("POSTGRES_PASSWORD", "test")
    container.with_env("POSTGRES_DB", "test_db")
    container.with_exposed_ports(5432)
    container.start()

    # Wait for PostgreSQL to become ready
    timeout = 30  # seconds
    start_time = time.time()

    while True:
        try:
            connection_url = f"postgresql://test:test@{container.get_container_host_ip()}:{container.get_exposed_port(5432)}/test_db"
            # Attempt to connect to the PostgreSQL server to verify it is ready
            import psycopg2
            conn = psycopg2.connect(connection_url)
            conn.close()
            print("PostgreSQL is ready.")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"PostgreSQL container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    yield container
    container.stop()


@pytest.fixture(scope='session')
def redis_container() -> DockerContainer:
    container = DockerContainer("redis:latest")
    container.with_exposed_ports(6379)
    container.start()

    # Wait for Redis to become ready
    timeout = 10  # seconds
    start_time = time.time()

    while True:
        try:
            import redis
            client = redis.Redis(
                host=container.get_container_host_ip(),
                port=container.get_exposed_port(6379),
            )
            client.ping()
            print("Redis is ready")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"Redis container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    yield container
    container.stop()


@pytest.fixture(scope='session')
def mongodb_container() -> DockerContainer:
    container = DockerContainer("mongo:latest")
    container.with_exposed_ports(27017)
    container.start()

    # Wait for MongoDB to become ready
    timeout = 10  # seconds
    start_time = time.time()

    while True:
        try:
            connection_url = f"mongodb://{container.get_container_host_ip()}:{container.get_exposed_port(27017)}"
            client = MongoClient(connection_url)
            # The ismaster command is fast and does not require auth.
            client.admin.command('ismaster')
            print("MongoDB is ready")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"MongoDB container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    yield container
    container.stop()


@pytest.fixture(scope='session')
def wiremock_container() -> DockerContainer:
    container = DockerContainer("wiremock/wiremock:latest")
    container.with_exposed_ports(8080)
    container.start()

    # Wait for Wiremock to become ready
    timeout = 10  # seconds
    start_time = time.time()

    while True:
        try:
            requests.get(f"http://{container.get_container_host_ip()}:{container.get_exposed_port(8080)}/__admin")
            print("Wiremock is ready")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"Wiremock container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    yield container
    container.stop()


@pytest.fixture(scope='function')
def wiremock_client(wiremock_container):
    base_url = f"http://{wiremock_container.get_container_host_ip()}:{wiremock_container.get_exposed_port(8080)}"
    wiremock_client = wiremock.WiremockClient(base_url)
    wiremock_client.verify_stub_creation()
    yield wiremock_client
    wiremock_client.reset()


@pytest.fixture(scope='session')
def api_client(postgres_container: DockerContainer,
               mongodb_container: DockerContainer,
               redis_container: DockerContainer) -> TestClient:
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = f"postgresql://test:test@{postgres_container.get_container_host_ip()}:{postgres_container.get_exposed_port(5432)}/test_db"
    os.environ['MONGO_URL'] = f"mongodb://{mongodb_container.get_container_host_ip()}:{mongodb_container.get_exposed_port(27017)}"
    os.environ['REDIS_URL'] = f'redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}'
    from app.main import app
    client = TestClient(app)
    yield client


@pytest.fixture(scope='session')
def celery(postgres_container: DockerContainer,
           mongodb_container: DockerContainer,
           redis_container: DockerContainer):
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DATABASE_URL'] = f"postgresql://test:test@{postgres_container.get_container_host_ip()}:{postgres_container.get_exposed_port(5432)}/test_db"
    os.environ['REDIS_URL'] = f'redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}'
    os.environ['MONGO_URL'] = f"mongodb://{mongodb_container.get_container_host_ip()}:{mongodb_container.get_exposed_port(27017)}"
    from app.tasks.celery_config import celery
    celery.conf.update(
        task_always_eager=True,
        broker_url=os.getenv('REDIS_URL'),
        result_backend=os.getenv('REDIS_URL'),
    )
    yield celery
