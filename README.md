# APIZIT Django REST Framework Heavy reference API

Run a predictable API locally and compare its behavior with the Flask,
FastAPI and Linking reference fixtures. This repository is standalone and MIT licensed.
The public Light repository and its private mirror contain identical files.

## Run locally

```sh
python -m venv .venv
# Activate .venv (Windows: .venv\Scripts\activate)
python -m pip install -r requirements-torch.txt
python -m pip install -r requirements-dev.txt
python manage.py runserver 127.0.0.1:8000 --noreload
```

The default URL is `http://127.0.0.1:8000`. No database, account or cloud credentials
are needed. This is a development fixture, not a production service.

## HTTP contract

| Method | Path |
| --- | --- |
| `GET` | `/health` |
| `GET` | `/info` |
| `POST` | `/echo` |
| `GET` | `/items/{item_id}` |
| `GET` | `/slow` |
| `GET` | `/ready` |
| `POST` | `/text/embedding` |
| `POST` | `/text/similarity` |
| `POST` | `/image/analyze` |
| `POST` | `/image/embedding` |

- `GET /health` returns exactly `{"status":"ok"}` without loading models.
- `GET /info` identifies `framework: "django"` and `profile: "heavy"`.
- `POST /echo` accepts `{"message":"hello","count":2}` and returns
  `{"received":{"message":"hello","count":2}}`. Count must be an integer,
  never a boolean; message must be a nonempty string.
- `GET /items/7?include_details=true` returns
  `{"item_id":7,"include_details":true,"details":"Reference item 7"}`.
  Details are omitted by default. IDs are positive integers; the query accepts true/false.
- `GET /slow` waits exactly **80 seconds**, then returns
  `{"delay_seconds":80,"status":"completed"}`. It is a duration probe, never a
  health check. Routine tests replace the sleep function; use `curl --max-time 90
  http://127.0.0.1:8000/slow` only for an intentional real-duration smoke.
- Invalid input receives a framework-native 4xx response. No caller-supplied URL,
  filesystem path or code is executed. All data is disposable.

```sh
curl http://127.0.0.1:8000/health
curl -H 'Content-Type: application/json' -d '{"message":"hello","count":2}' http://127.0.0.1:8000/echo
curl 'http://127.0.0.1:8000/items/7?include_details=true'
```

## Heavy workload

The same lazy CPU Sentence Transformer and ResNet50 services as the Python Heavy
fixtures use PyTorch, torchvision, Transformers, Sentence Transformers, NumPy,
SciPy, scikit-learn, OpenCV and Pillow. Health does not instantiate models.
`/ready` loads both services and returns 200 ready or 503 unavailable.
Text endpoints accept `{"text":"hello"}` or `{"left":"hello","right":"world"}`.
Embedding responses contain model, dimension and embedding; similarity returns
model and cosine similarity. Image endpoints accept multipart field `file` with
JPEG/PNG/WebP, at most 4 MiB and 20 million pixels. Analyze returns model, image
dimensions/format and predictions; embedding returns model, dimension and embedding.
Text is limited to 5000 characters. Models download public weights lazily into
`MODEL_CACHE_DIR` (a temporary-directory cache by default); normal CI uses controlled model doubles. `pytest -q -m model` is an
explicit network/model smoke and may take several minutes.


## APIZIT qualification status

The matching platform adapter and hosted launch path are being qualified in the
APIZIT development environment. Local tests and a published fixture do not prove
a hosted launch. Follow the platform's reference qualification evidence for the
exact source commits and observed results. This fixture needs no APIZIT checkout.

The measured scan and current backend commercial catalog determine launch eligibility.
No deployment profile, paid plan or production readiness is promised by this repository.

See CONTRIBUTING.md for repeatable checks.

This stateless public fixture accepts its assigned host by default. Set
`APP_ALLOWED_HOSTS` to a comma-separated allowlist when testing host restrictions.
It has no sessions, authentication, persistent data or host-dependent redirects.
