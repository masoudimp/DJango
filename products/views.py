from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST

from .forms import TagForm
from .models import Tag


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
        "tag_form": tag_form,
    }, status=400 if tag_form is not None else 200)


def management(request, tag_form=None):
    # Products and categories are samples; tags come from the database.
    sections = [
        {"key": "product", "title": "Products", "detail_label": "Category", "rows": [
            {"id": 1, "title": "Cordless drill", "detail": "Power tools", "category": "power-tools", "tags": "Cordless|Compact", "description": "Compact cordless drill for everyday installation and assembly work."},
            {"id": 2, "title": "Safety helmet", "detail": "Safety equipment", "category": "safety", "tags": "Lightweight", "description": "Comfortable head protection for work on site."},
            {"id": 3, "title": "Storage case", "detail": "Storage", "category": "storage", "tags": "Compact", "description": "Organize small parts and essential accessories."},
        ]},
        {"key": "category", "title": "Categories", "detail_label": "Parent category", "rows": [
            {"id": 1, "title": "Tools", "detail": "—", "category": ""},
            {"id": 2, "title": "Power tools", "detail": "Tools", "category": "tools"},
            {"id": 3, "title": "Drills", "detail": "Power tools", "category": "power-tools"},
        ]},
        {"key": "tag", "title": "Tags", "rows": Tag.objects.order_by("title", "id")},
    ]
    return render(request, "products/management.html", {
        "sections": sections,
        "demo_tags": ["Cordless", "Compact", "Lightweight", "Heavy duty", "Professional"],
        "management": True,
        "active_section": "tag" if tag_form is not None else request.GET.get("section", "product"),
        "tag_form": tag_form,
    }, status=400 if tag_form is not None else 200)
