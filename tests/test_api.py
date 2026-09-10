import json
from pathlib import Path

import pytest
from django.urls import get_resolver


def test_exact_routes():
    contract = json.loads(Path("contract.json").read_text())
    paths = {
        "/" + str(route.pattern).replace("<int:item_id>", "{item_id}")
        for route in get_resolver().url_patterns
    }
    assert paths == {route["path"] for route in contract["routes"]}


def test_health_and_info(client, monkeypatch):
    monkeypatch.setattr("app.views.sleep", lambda _: pytest.fail("Health must not sleep"))
    assert client.get("/health").json() == {"status": "ok"}
    contract = json.loads(Path("contract.json").read_text())
    assert client.get("/info").json() == {key: contract[key] for key in ("framework", "profile")}
    assert client.post("/health").status_code == 405


def test_echo(client):
    payload = {"message": "hello", "count": 2}
    response = client.post("/echo", payload, format="json")
    assert response.status_code == 200
    assert response.json() == {"received": payload}


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"message": "", "count": 1},
        {"message": "x", "count": True},
        {"message": "x", "count": 1.5},
        {"message": "x" * 5001, "count": 1},
    ],
)
def test_invalid_echo(client, payload):
    assert (
        client.post("/echo", json.dumps(payload), content_type="application/json").status_code
        == 400
    )


def test_invalid_json(client):
    assert client.post("/echo", "{", content_type="application/json").status_code == 400


def test_items(client):
    assert client.get("/items/7").json() == {"item_id": 7, "include_details": False}
    assert client.get("/items/7?include_details=true").json() == {
        "item_id": 7,
        "include_details": True,
        "details": "Reference item 7",
    }


@pytest.mark.parametrize(
    "path", ["/items/0", "/items/-1", "/items/abc", "/items/7?include_details=maybe"]
)
def test_invalid_items(client, path):
    assert client.get(path).status_code in {400, 404}


def test_slow(client, monkeypatch):
    durations = []
    monkeypatch.setattr("app.views.sleep", durations.append)
    assert client.get("/slow").json() == {"delay_seconds": 80, "status": "completed"}
    assert durations == [80]
