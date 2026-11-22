from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("manage/", views.management, name="management"),
    path("categories/create/", views.create_category, name="create_category"),
    path("categories/<int:pk>/edit/", views.edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", views.delete_category, name="delete_category"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("products/<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("tags/create/", views.create_tag, name="create_tag"),
    path("tags/<int:pk>/edit/", views.edit_tag, name="edit_tag"),
    path("tags/<int:pk>/delete/", views.delete_tag, name="delete_tag"),
]
