import json
import logging

from app.logging_conf import JsonFormatter


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_when_db_up(client):
    assert client.get("/ready").status_code == 200


def test_version_endpoint(client):
    assert client.get("/version").json() == {"version": "test-1.0.0"}


def test_create_and_fetch_operation(client):
    created = client.post("/operations", json={"name": "deploy-check"})
    assert created.status_code == 201
    op_id = created.json()["id"]
    fetched = client.get(f"/operations/{op_id}")
    assert fetched.json()["name"] == "deploy-check"


def test_missing_operation_returns_404(client):
    assert client.get("/operations/9999").status_code == 404


def test_empty_name_rejected(client):
    assert client.post("/operations", json={"name": ""}).status_code == 422


def test_metrics_exposes_request_counter(client):
    client.get("/health")
    body = client.get("/metrics").text
    assert "http_requests_total" in body


def test_log_formatter_outputs_valid_json():
    record = logging.LogRecord("apex", logging.INFO, "", 0, "hello", None, None)
    record.fields = {"status": 200}
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["msg"] == "hello" and parsed["status"] == 200
