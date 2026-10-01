from fastapi.testclient import TestClient

from app.main import app


def test_calculation_history_and_deletion(tmp_path, monkeypatch):
    database_path = tmp_path / "test-calculator.db"
    monkeypatch.setenv("CALCULATOR_DB_PATH", str(database_path))

    with TestClient(app) as client:
        calculation = client.post("/api/calculate", json={"expression": "(2+3)*4"})
        assert calculation.status_code == 200
        body = calculation.json()
        assert body["success"] is True
        assert body["result"] == 20

        history = client.get("/api/history")
        assert history.status_code == 200
        items = history.json()["items"]
        assert len(items) == 1
        assert items[0]["expression"] == "(2+3)*4"

        deletion = client.delete(f"/api/history/{items[0]['id']}")
        assert deletion.status_code == 200

        empty_history = client.get("/api/history")
        assert empty_history.json()["items"] == []


def test_invalid_expression_is_not_saved(tmp_path, monkeypatch):
    database_path = tmp_path / "test-invalid.db"
    monkeypatch.setenv("CALCULATOR_DB_PATH", str(database_path))

    with TestClient(app) as client:
        response = client.post("/api/calculate", json={"expression": "1/0"})
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert client.get("/api/history").json()["items"] == []

