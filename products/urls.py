from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("manage/", views.management, name="management"),
    path("tags/create/", views.create_tag, name="create_tag"),
    path("tags/<int:pk>/delete/", views.delete_tag, name="delete_tag"),
]
