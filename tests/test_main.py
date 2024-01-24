from app import main
from fastapi.testclient import TestClient

test_api_client = TestClient(main.app)


def test_index():
    response = test_api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, world!'}
