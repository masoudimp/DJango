from django.db.models import Q

from .dtos import ProductFilterRequest
from .models import Category, Product


def filter_products(filters: ProductFilterRequest):
    products = Product.objects.select_related("category", "image").prefetch_related("tags")

    if filters.categoryId is not None:
        # Include descendants when a parent category is selected.
        children = {}
        for category_id, parent_id in Category.objects.values_list("id", "parent_id"):
            children.setdefault(parent_id, []).append(category_id)
        category_ids = {filters.categoryId}
        pending = [filters.categoryId]
        while pending:
            for child_id in children.get(pending.pop(), []):
                if child_id not in category_ids:
                    category_ids.add(child_id)
                    pending.append(child_id)
        products = products.filter(category_id__in=category_ids)

    if filters.tagIds:
        # ANY selected tag matches; distinct prevents duplicate product cards.
        products = products.filter(tags__id__in=filters.tagIds).distinct()

    if filters.search:
        products = products.filter(
            Q(title__icontains=filters.search) | Q(description__icontains=filters.search)
        )

    return products.order_by("title", "id")
