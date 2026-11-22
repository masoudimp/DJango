from django.contrib import admin

from .forms import CategoryForm
from .models import Category, Product, Tag


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ("title", "description", "category", "tags")
    list_display = ("id", "title", "category")
    list_filter = ("category", "tags")
    search_fields = ("title", "description")
    list_select_related = ("category",)
    filter_horizontal = ("tags",)
    ordering = ("title", "id")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ("id", "title", "parent")
    search_fields = ("title",)
    list_select_related = ("parent",)
    ordering = ("title", "id")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("title", "id")
