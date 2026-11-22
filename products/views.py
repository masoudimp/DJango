from django.shortcuts import render


def dashboard(request):
    products = [
        {"title": "Cordless drill", "category": "Power tools", "description": "Compact cordless drill for everyday installation and assembly work. Its comfortable grip and adjustable speed help with precise drilling, while the lightweight design makes it easy to carry between jobs.", "image": None, "tags": ["Cordless", "Heavy duty", "Professional", "Compact"]},
        {"title": "Safety helmet", "category": "Safety equipment", "description": "A practical safety helmet for everyday work on site. The adjustable fit and comfortable interior make it suitable for extended use, with a lightweight shell that is easy to store alongside other protective equipment.", "image": None},
        {"title": "Cable reel", "category": "Electrical", "description": "Keep cables organized and ready for the next job with this portable cable reel. The sturdy frame and convenient handle make transport simple, while the winding design helps reduce tangles during storage.", "image": None},
        {"title": "Adjustable wrench", "category": "Hand tools", "description": "A versatile adjustable wrench for assembly, repairs, and routine maintenance. The adjustable jaw accommodates different fastener sizes, and the comfortable handle provides control when working in tight spaces.", "image": None},
        {"title": "Work gloves", "category": "Safety equipment", "description": "Comfortable work gloves for handling tools, supplies, and materials throughout the day. Their flexible construction supports a secure grip and freedom of movement, making them a useful addition to an everyday work kit.", "image": None},
        {"title": "Storage case", "category": "Storage", "description": "Organize small parts and essential accessories in a convenient storage case. Separate compartments keep items easy to find, while the compact design fits neatly on a shelf or travels with the rest of your equipment.", "image": None},
    ]
    demo_tags = [
        "Cordless", "Heavy duty", "Portable", "Indoor", "Outdoor",
        "Reusable", "Lightweight", "Professional", "Compact", "Essential",
    ]
    return render(request, "products/dashboard.html", {"products": products, "demo_tags": demo_tags})
