import os

from loguru import logger
from sqlmodel import select
from uuid import uuid4
from app.models.test import TestTable
from app.config import ConfigManager
import random
import requests


def test_index(api_client):
    response = api_client.get("/")
    assert response.status_code == 200


def test_health(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    assert response.json().get("infrastructure").get("database")
    assert response.json().get("infrastructure").get("redis")
    assert response.json().get("infrastructure").get("mongodb")


def test_db_adapter():
    id = int(random.randint(1, 1000))
    name = str(uuid4())

    db_instance = ConfigManager.get_postgres_adapter()

    test_instance = TestTable(id=id, name=name)
    with db_instance.get_session() as session:
        session.add(test_instance)
        session.commit()

    # Example get (select) query by primary key
    with db_instance.get_session() as session:
        retrieved_instance = session.get(TestTable, id)
        logger.info(f"Retrieved instance: {retrieved_instance}")
        assert retrieved_instance.id == id
        assert retrieved_instance.name == name

    # Example query with filters
    with db_instance.get_session() as session:
        statement = select(TestTable).where(TestTable.name == name)
        result = session.exec(statement).all()
        logger.info(f"Query result: {result}")
        assert len(result) == 1
        assert result[0].id == id
        assert result[0].name == name

    # Example delete query
    with db_instance.get_session() as session:
        if retrieved_instance:
            session.delete(retrieved_instance)
            session.commit()
            logger.info(f"Deleted instance with id: {retrieved_instance.id}")
            assert session.get(TestTable, retrieved_instance.id) is None


def test_celery(celery):
    from app.tasks import task_definitions
    job = task_definitions.add.delay(1, 2)
    assert job.id
    assert job.status
    assert job.result
    assert job.result == 3
    assert job.status == "SUCCESS"


def test_redis(api_client):
    redis_instance = ConfigManager.get_redis_adapter()
    key = str(uuid4())
    value = str(uuid4())
    redis_instance.set(key, value)
    assert redis_instance.get(key) == value
    redis_instance.delete(key)
    assert redis_instance.get(key) is None


def test_wiremock_client(wiremock_client):
    mock_url = wiremock_client.stub(
        method="GET",
        url="/external/api/endpoint",
        status_code=200,
        response_body={"data": "Hello, world!"},
        response_headers={"Content-Type": "application/json"}
    )

    response = requests.get(mock_url)
    assert response.status_code == 200
    assert response.json() == {"data": "Hello, world!"}


def test_random(api_client, wiremock_client):
    os.environ['RANDOM_UUID_BASE_URL'] = wiremock_client.get_base_url()
    wiremock_client.stub(
        method="GET",
        url="/uuid",
        status_code=200,
        response_body={"uuid": 1234567890},
        response_headers={"Content-Type": "application/json"}
    )
    random_response = api_client.get("/random")
    assert random_response.json() == {"uuid": 1234567890}
