from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError

from .forms import CategoryForm, ProductForm, TagForm
from .models import Category, Product, Tag


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


@require_POST
def create_tag(request):
    form = TagForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                tag = form.save()
        except IntegrityError:
            form.add_error("title", "A tag with this title already exists.")
        else:
            messages.success(request, "Tag added successfully")
            return redirect("/manage/?section=tag")
    return management(request, tag_form=form)


@require_POST
def edit_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    form = TagForm(request.POST, instance=tag)
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error("title", "A tag with this title already exists.")
        else:
            messages.success(request, "Tag updated successfully.")
            return redirect("/manage/?section=tag")
    return management(request, tag_form=form)


@require_POST
def delete_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    messages.success(request, "Tag deleted successfully.")
    return redirect("/manage/?section=tag")


@require_POST
def create_category(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error("title", "A category with this title already exists.")
        else:
            messages.success(request, "Category added successfully.")
            return redirect("/manage/?section=category")
    return management(request, category_form=form)


@require_POST
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error("title", "A category with this title already exists.")
        else:
            messages.success(request, "Category updated successfully.")
            return redirect("/manage/?section=category")
    return management(request, category_form=form)


@require_POST
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    try:
        category.delete()
    except ProtectedError:
        return management(request, category_error="This category has subcategories or products. Move or delete them first.")
    messages.success(request, "Category deleted successfully.")
    return redirect("/manage/?section=category")


@require_POST
def create_product(request):
    form = ProductForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, "Product added successfully.")
        return redirect("/manage/?section=product")
    return management(request, product_form=form)


@require_POST
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST, instance=product)
    if form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("/manage/?section=product")
    return management(request, product_form=form)


@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect("/manage/?section=product")


def dashboard(request):
    return render(request, "products/dashboard.html", {
        "products": Product.objects.select_related("category", "image").prefetch_related("tags").order_by("title", "id"),
        "demo_tags": Tag.objects.order_by("title", "id"),
        "categories": category_tree(),
    })


def management(request, tag_form=None, category_form=None, category_error=None, product_form=None):
    sections = [
        {"key": "product", "title": "Products", "detail_label": "Category",
         "rows": Product.objects.select_related("category").prefetch_related("tags").order_by("title", "id")},
        {"key": "category", "title": "Categories", "detail_label": "Parent category",
         "rows": Category.objects.select_related("parent").order_by("title", "id")},
        {"key": "tag", "title": "Tags", "rows": Tag.objects.order_by("title", "id")},
    ]
    return render(request, "products/management.html", {
        "sections": sections,
        "demo_tags": Tag.objects.order_by("title", "id"),
        "product_form": product_form,
        "selected_tag_ids": product_form["tags"].value() if product_form is not None else [],
        "management": True,
        "active_section": "product" if product_form is not None else "category" if category_form is not None or category_error else "tag" if tag_form is not None else request.GET.get("section", "product"),
        "categories": category_tree(),
        "category_form": category_form,
        "category_error": category_error,
        "tag_form": tag_form,
    }, status=400 if tag_form is not None or category_form is not None or category_error or product_form is not None else 200)
