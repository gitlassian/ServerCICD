from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # Since it returns a FileResponse, we can't easily check content without mocks or files
    # but status 200 is a good start.

def test_get_messages():
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
