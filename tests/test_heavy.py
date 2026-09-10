from io import BytesIO
from types import SimpleNamespace

import numpy as np
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from app.errors import ModelUnavailableError


@pytest.fixture(autouse=True)
def controlled_models(monkeypatch):
    text = SimpleNamespace(
        model_id="text-double",
        embed=lambda values: np.array([[0.25, 0.5, 0.75] for _ in values]),
        similarity=lambda _a, _b: 0.8125,
    )
    image = SimpleNamespace(
        model_id="image-double",
        embed=lambda _: np.arange(8, dtype=float),
        classify=lambda _: [{"label": "orange", "score": 0.8}],
    )
    monkeypatch.setattr(
        "app.views.registry",
        lambda: SimpleNamespace(get=lambda name: {"text": text, "image": image}[name]),
    )


def upload():
    buffer = BytesIO()
    Image.new("RGB", (24, 16), "orange").save(buffer, "PNG")
    return SimpleUploadedFile("sample.png", buffer.getvalue(), content_type="image/png")


def test_health_does_not_load_models(client, monkeypatch):
    monkeypatch.setattr("app.views.registry", lambda: pytest.fail("Unexpected model load"))
    assert client.get("/health").status_code == 200


def test_ready_and_unavailable(client, monkeypatch):
    assert client.get("/ready").json()["status"] == "ready"

    def fail(_name):
        raise ModelUnavailableError("Controlled failure")

    monkeypatch.setattr("app.views.registry", lambda: SimpleNamespace(get=fail))
    assert client.get("/ready").status_code == 503
    assert client.post("/text/embedding", {"text": "hello"}, format="json").status_code == 503


def test_text(client):
    assert client.post("/text/embedding", {"text": "hello"}, format="json").json() == {
        "model": "text-double",
        "dimension": 3,
        "embedding": [0.25, 0.5, 0.75],
    }
    assert (
        client.post("/text/similarity", {"left": "hello", "right": "world"}, format="json").json()[
            "similarity"
        ]
        == 0.8125
    )


@pytest.mark.parametrize("payload", [{}, {"text": 123}, {"text": "   "}, {"text": "x" * 5001}])
def test_text_validation(client, payload):
    assert client.post("/text/embedding", payload, format="json").status_code == 400


def test_images(client):
    analyzed = client.post("/image/analyze", {"file": upload()}, format="multipart")
    assert analyzed.status_code == 200
    assert analyzed.json()["image"] == {"width": 24, "height": 16, "format": "PNG"}
    assert analyzed.json()["predictions"] == [{"label": "orange", "score": 0.8}]
    embedded = client.post("/image/embedding", {"file": upload()}, format="multipart").json()
    assert embedded["dimension"] == len(embedded["embedding"]) == 8


@pytest.mark.parametrize(
    ("data", "mime", "status"),
    [
        (b"bad", "text/plain", 415),
        (b"bad", "image/png", 400),
        (b"x" * (4 * 1024 * 1024 + 1), "image/png", 413),
    ],
    ids=["unsupported-media", "invalid-image", "oversized-image"],
)
def test_image_validation(client, data, mime, status):
    file = SimpleUploadedFile("sample", data, content_type=mime)
    assert client.post("/image/analyze", {"file": file}, format="multipart").status_code == status
    assert client.post("/image/embedding", {}, format="multipart").status_code == 400
