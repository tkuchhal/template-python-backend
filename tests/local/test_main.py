from loguru import logger
from sqlmodel import select


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

#
# def test_db_adapter():
#     test_instance = TestTable(id=1, name="test_name")
#     with db_instance.get_session() as session:
#         session.add(test_instance)
#         session.commit()
#     # Example get (select) query by primary key
#     with db_instance.get_session() as session:
#         retrieved_instance = session.get(TestTable, 1)
#         logger.info(f"Retrieved instance: {retrieved_instance}")
#     # Example query with filters
#     with db_instance.get_session() as session:
#         statement = select(TestTable).where(TestTable.name == "test_name")
#         result = session.exec(statement).all()
#         logger.info(f"Query result: {result}")
#     # Example delete query
#     with db_instance.get_session() as session:
#         if retrieved_instance:
#             session.delete(retrieved_instance)
#             session.commit()
#             logger.info(f"Deleted instance with id: {retrieved_instance.id}")
