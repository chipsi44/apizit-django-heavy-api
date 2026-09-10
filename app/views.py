from time import sleep

from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

SLOW_RESPONSE_SECONDS = 80


def text_field(payload, field):
    if not isinstance(payload, dict):
        raise ValidationError("Expected a JSON object.")
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip() or len(value) > 5000:
        raise ValidationError(f"'{field}' must be a nonempty string of at most 5000 characters.")
    return value


@api_view(["GET"])
def health(_request):
    return Response({"status": "ok"})


@api_view(["GET"])
def info(_request):
    return Response({"framework": "django", "profile": "heavy"})


@api_view(["POST"])
def echo(request):
    message = text_field(request.data, "message")
    count = request.data.get("count")
    if not isinstance(count, int) or isinstance(count, bool):
        raise ValidationError("'count' must be an integer.")
    return Response({"received": {"message": message, "count": count}})


@api_view(["GET"])
def item(request, item_id):
    raw = request.query_params.get("include_details", "false").lower()
    if item_id < 1 or raw not in {"true", "false"}:
        raise ValidationError("Expected a positive item ID and true/false include_details.")
    result = {"item_id": item_id, "include_details": raw == "true"}
    if result["include_details"]:
        result["details"] = f"Reference item {item_id}"
    return Response(result)


@api_view(["GET"])
def slow(_request):
    sleep(SLOW_RESPONSE_SECONDS)
    return Response({"delay_seconds": SLOW_RESPONSE_SECONDS, "status": "completed"})


def registry():
    # Import the heavy dependency graph only when an inference route is used.
    from app.heavy import model_registry

    return model_registry


def model_call(operation):
    from app.errors import APIError, error_payload

    try:
        return Response(operation())
    except APIError as error:
        return Response(error_payload(error.code, error.message), status=error.status_code)


@api_view(["GET"])
def ready(_request):
    from app.errors import ModelUnavailableError

    states = {}
    for name in ("text", "image"):
        try:
            registry().get(name)
            states[name] = True
        except ModelUnavailableError:
            states[name] = False
    available = all(states.values())
    return Response(
        {"status": "ready" if available else "unavailable", "models": states, "device": "cpu"},
        status=200 if available else 503,
    )


def embedding_result(service, value):
    vector = service.embed(value)
    return {"model": service.model_id, "dimension": len(vector), "embedding": vector.tolist()}


@api_view(["POST"])
def text_embedding(request):
    text = text_field(request.data, "text")

    def operation():
        service = registry().get("text")
        vector = service.embed([text])[0]
        return {"model": service.model_id, "dimension": len(vector), "embedding": vector.tolist()}

    return model_call(operation)


@api_view(["POST"])
def text_similarity(request):
    left, right = text_field(request.data, "left"), text_field(request.data, "right")

    def operation():
        service = registry().get("text")
        return {"model": service.model_id, "similarity": service.similarity(left, right)}

    return model_call(operation)


def uploaded_image(request):
    from app.config import Settings
    from app.ml import decode_image

    upload = request.FILES.get("file")
    if upload is None:
        raise ValidationError("Multipart field 'file' is required.")
    settings = Settings()
    return decode_image(upload.read(settings.max_upload_bytes + 1), upload.content_type, settings)


@api_view(["POST"])
def image_analyze(request):
    def operation():
        decoded = uploaded_image(request)
        service = registry().get("image")
        return {
            "model": service.model_id,
            "image": {"width": decoded.width, "height": decoded.height, "format": decoded.format},
            "predictions": service.classify(decoded),
        }

    return model_call(operation)


@api_view(["POST"])
def image_embedding(request):
    def operation():
        decoded = uploaded_image(request)
        return embedding_result(registry().get("image"), decoded)

    return model_call(operation)
