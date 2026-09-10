from django.urls import path

from app import views

urlpatterns = [
    path("health", views.health),
    path("info", views.info),
    path("echo", views.echo),
    path("items/<int:item_id>", views.item),
    path("slow", views.slow),
    path("ready", views.ready),
    path("text/embedding", views.text_embedding),
    path("text/similarity", views.text_similarity),
    path("image/analyze", views.image_analyze),
    path("image/embedding", views.image_embedding),
]
