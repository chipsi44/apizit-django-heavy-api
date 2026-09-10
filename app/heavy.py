from app.config import Settings
from app.ml import ImageService, ModelRegistry, TextService

settings = Settings()
model_registry = ModelRegistry()
model_registry.register("text", lambda: TextService(settings))
model_registry.register("image", lambda: ImageService(settings))
