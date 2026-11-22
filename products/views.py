from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError

from .forms import CategoryForm, TagForm
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


def dashboard(request, tag_form=None):
    products = [
        {"title": "Cordless drill", "category": "Power tools", "description": "Compact cordless drill for everyday installation and assembly work. Its comfortable grip and adjustable speed help with precise drilling, while the lightweight design makes it easy to carry between jobs.", "image": None, "tags": ["Cordless", "Heavy duty", "Professional", "Compact"]},
        {"title": "Safety helmet", "category": "Safety equipment", "description": "A practical safety helmet for everyday work on site. The adjustable fit and comfortable interior make it suitable for extended use, with a lightweight shell that is easy to store alongside other protective equipment.", "image": None},
        {"title": "Cable reel", "category": "Electrical", "description": "Keep cables organized and ready for the next job with this portable cable reel. The sturdy frame and convenient handle make transport simple, while the winding design helps reduce tangles during storage.", "image": None},
        {"title": "Adjustable wrench", "category": "Hand tools", "description": "A versatile adjustable wrench for assembly, repairs, and routine maintenance. The adjustable jaw accommodates different fastener sizes, and the comfortable handle provides control when working in tight spaces.", "image": None},
        {"title": "Work gloves", "category": "Safety equipment", "description": "Comfortable work gloves for handling tools, supplies, and materials throughout the day. Their flexible construction supports a secure grip and freedom of movement, making them a useful addition to an everyday work kit.", "image": None},
        {"title": "Storage case", "category": "Storage", "description": "Organize small parts and essential accessories in a convenient storage case. Separate compartments keep items easy to find, while the compact design fits neatly on a shelf or travels with the rest of your equipment.", "image": None},
    ]
    demo_tags = list(Tag.objects.order_by("title").values_list("title", flat=True))
    return render(request, "products/dashboard.html", {
        "products": products,
        "demo_tags": demo_tags,
        "categories": category_tree(),
        "tag_form": tag_form,
    }, status=400 if tag_form is not None else 200)


def management(request, tag_form=None, category_form=None, category_error=None):
    # Products are samples; categories and tags come from the database.
    sections = [
        {"key": "product", "title": "Products", "detail_label": "Category", "rows": [
            {"id": 1, "title": "Cordless drill", "detail": "Power tools", "category": "power-tools", "tags": "Cordless|Compact", "description": "Compact cordless drill for everyday installation and assembly work."},
            {"id": 2, "title": "Safety helmet", "detail": "Safety equipment", "category": "safety", "tags": "Lightweight", "description": "Comfortable head protection for work on site."},
            {"id": 3, "title": "Storage case", "detail": "Storage", "category": "storage", "tags": "Compact", "description": "Organize small parts and essential accessories."},
        ]},
        {"key": "category", "title": "Categories", "detail_label": "Parent category",
         "rows": Category.objects.select_related("parent").order_by("title", "id")},
        {"key": "tag", "title": "Tags", "rows": Tag.objects.order_by("title", "id")},
    ]
    return render(request, "products/management.html", {
        "sections": sections,
        "demo_tags": ["Cordless", "Compact", "Lightweight", "Heavy duty", "Professional"],
        "management": True,
        "active_section": "category" if category_form is not None or category_error else "tag" if tag_form is not None else request.GET.get("section", "product"),
        "categories": category_tree(),
        "category_form": category_form,
        "category_error": category_error,
        "tag_form": tag_form,
    }, status=400 if tag_form is not None or category_form is not None or category_error else 200)
