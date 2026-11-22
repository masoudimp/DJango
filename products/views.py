from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .dtos import ProductFilterRequest
from .filters import filter_products
from .models import Category, Tag


def category_tree():
    categories = list(Category.objects.order_by("title", "id"))
    by_id = {category.pk: category for category in categories}
    roots = []
    for category in categories:
        category.picker_children = []
    for category in categories:
        if category.parent_id in by_id:
            by_id[category.parent_id].picker_children.append(category)
        else:
            roots.append(category)
    return roots


def dashboard(request):
    return render(request, "products/dashboard.html", {
        "products": filter_products(ProductFilterRequest()),
        "demo_tags": Tag.objects.order_by("title", "id"),
        "categories": category_tree(),
    })


@require_GET
def product_list(request):
    try:
        filters = ProductFilterRequest.from_query(request.GET)
    except ValueError:
        return JsonResponse({"error": "Category and tag IDs must be positive integers."}, status=400)
    return render(request, "products/includes/product_list.html", {
        "products": filter_products(filters),
    })
