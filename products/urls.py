from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("tags/create/", views.create_tag, name="create_tag"),
]
