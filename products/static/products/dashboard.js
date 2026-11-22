document.documentElement.dataset.inputMode = "pointer";
const productImageInput = document.getElementById("new-product-image");
document.getElementById("upload-product-image")?.addEventListener("click", () => productImageInput.click());
productImageInput?.addEventListener("change", () => {
    document.getElementById("product-image-name").textContent = productImageInput.files[0]?.name || "";
});
document.querySelectorAll('.admin-demo-form:not(#create-tag-form):not(#create-category-form)').forEach((form) => {
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const category = form.querySelector('input[name="category"]');
        if (category && !category.value) {
            form.querySelector(".admin-form-status").textContent = "Please select a category.";
            form.querySelector('[data-picker="category"] button').focus();
            return;
        }
        form.querySelector(".admin-form-status").textContent = "";
        showAddSuccess(form);
    });
});
const productModalElement = document.getElementById("product-modal");
const productModal = productModalElement ? new bootstrap.Modal(productModalElement) : null;
let activeProductCard = null;
function openProductModal(card) {
    activeProductCard = card;
    document.getElementById("product-modal-title").textContent = card.querySelector(".product-title").textContent;
    const image = card.querySelector(".product-image");
    const modalImage = document.getElementById("product-modal-image");
    modalImage.src = image.src;
    modalImage.alt = image.alt;
    const modalDescription = document.getElementById("product-modal-description");
    const description = card.querySelector(".product-description").textContent;
    modalDescription.textContent = description;
    document.getElementById("product-modal-labels").replaceChildren(
        ...[...card.querySelectorAll(".badge-track .badge")].map((badge) => badge.cloneNode(true)),
    );
    document.querySelectorAll(".product-description").forEach((element) => bootstrap.Tooltip.getInstance(element)?.hide());
    productModal.show();
}
document.querySelectorAll(".product-card").forEach((card) => {
    card.addEventListener("click", (event) => {
        if (event.target.closest("button, a, input")) return;
        openProductModal(card);
    });
    card.addEventListener("keydown", (event) => {
        if (event.target === card && ["Enter", " "].includes(event.key)) {
            event.preventDefault();
            openProductModal(card);
        }
    });
});
productModalElement?.addEventListener("hidden.bs.modal", () => activeProductCard?.focus({ preventScroll: true }));
document.querySelectorAll(".badge-rail").forEach((rail) => {
    const track = rail.querySelector(".badge-track");
    const buttons = [...rail.querySelectorAll(".badge-scroll")];
    const update = () => {
        // Include the space occupied by the controls when deciding if they are needed.
        const overflow = track.scrollWidth > rail.clientWidth + 1;
        buttons.forEach((button) => {
            button.hidden = !overflow;
            button.disabled = button.dataset.scroll === "-1"
                ? track.scrollLeft <= 1
                : track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;
        });
    };
    buttons.forEach((button) => button.addEventListener("click", () => {
        track.scrollBy({
            left: Number(button.dataset.scroll) * Math.max(80, track.clientWidth * 0.75),
            behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth",
        });
    }));
    track.addEventListener("scroll", update, { passive: true });
    new ResizeObserver(update).observe(rail);
    update();
});
document.querySelectorAll('.product-description[data-bs-toggle="tooltip"]').forEach((element) => {
    new bootstrap.Tooltip(element, {
        container: "body",
        trigger: "hover focus",
        customClass: "product-description-tooltip",
        html: false,
    });
});
document.addEventListener("pointerdown", () => {
    document.documentElement.dataset.inputMode = "pointer";
}, true);
document.addEventListener("keydown", (event) => {
    if (["Tab", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " ", "Enter"].includes(event.key)) {
        document.documentElement.dataset.inputMode = "keyboard";
    }
}, true);

const contactButton = document.getElementById("contact-info");
const contactPopover = new bootstrap.Popover(contactButton, {
    content: () => document.getElementById("contact-content").content.firstElementChild.cloneNode(true),
    html: true,
    placement: "top",
    fallbackPlacements: ["bottom", "right", "left"],
    trigger: "click",
    container: "body",
    customClass: "contact-popover",
    offset: [0, 12],
});

contactButton.addEventListener("shown.bs.popover", () => contactButton.setAttribute("aria-expanded", "true"));
contactButton.addEventListener("hidden.bs.popover", () => contactButton.setAttribute("aria-expanded", "false"));
document.addEventListener("click", (event) => {
    if (!contactButton.contains(event.target) && !event.target.closest(".contact-popover")) {
        contactPopover.hide();
    }
});
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") contactPopover.hide();
});

document.querySelectorAll('[data-picker="tags"]').forEach((root) => {
    const getElement = (id) => document.getElementById(root.dataset.prefix + id);
const tagInputs = [...root.querySelectorAll('.tag-options input[type="checkbox"]')];
const tagsSummary = getElement("tags-summary");
const emptySummary = tagsSummary.textContent;
function updateTagsSummary() {
    const selected = tagInputs.filter((input) => input.checked);
    tagsSummary.textContent = selected.length === 0 ? emptySummary
        : selected.length === 1 ? selected[0].value : `${selected.length} tags selected`;
}
tagInputs.forEach((input) => input.addEventListener("change", updateTagsSummary));
getElement("clear-tags").addEventListener("click", () => {
    tagInputs.forEach((input) => { input.checked = false; });
    updateTagsSummary();
});
updateTagsSummary();

const tagSearch = getElement("tag-search");
tagSearch.addEventListener("input", () => {
    const query = tagSearch.value.trim().toLowerCase();
    let matches = 0;
    tagInputs.forEach((input) => {
        const visible = input.value.toLowerCase().includes(query);
        input.closest(".tag-option").hidden = !visible;
        if (visible) matches += 1;
    });
    getElement("tag-no-results").hidden = matches > 0;
});


});

document.querySelectorAll('[data-picker="category"]').forEach((root) => {
    const getElement = (id) => document.getElementById(root.dataset.prefix + id);
const categoryOptions = root.querySelectorAll("[data-category]");
const selectedOption = [...categoryOptions].find((option) => option.dataset.category === getElement("category-value").value);
if (selectedOption) {
    getElement("category-summary").textContent = selectedOption.textContent;
    categoryOptions.forEach((option) => {
        option.classList.toggle("active", option === selectedOption);
        if (option === selectedOption) option.setAttribute("aria-current", "true");
        else option.removeAttribute("aria-current");
    });
}

categoryOptions.forEach((option) => {
    option.addEventListener("click", () => {
        getElement("category-summary").textContent = option.textContent;
        getElement("category-value").value = option.dataset.category;
        categoryOptions.forEach((item) => {
            item.classList.remove("active");
            item.removeAttribute("aria-current");
        });
        option.classList.add("active");
        option.setAttribute("aria-current", "true");
        const trigger = getElement("category");
        if (trigger.dataset.bsToggle === "dropdown") {
            bootstrap.Dropdown.getOrCreateInstance(trigger).hide();
            trigger.focus();
        }
    });
});

function syncCategoryBranch(toggle) {
    const children = document.getElementById(toggle.getAttribute("aria-controls"));
    const collapse = bootstrap.Collapse.getOrCreateInstance(children, { toggle: false });
    if (toggle.getAttribute("aria-expanded") === "true") collapse.show();
    else collapse.hide();
}

root.querySelectorAll(".category-toggle").forEach((toggle) => {
    const children = document.getElementById(toggle.getAttribute("aria-controls"));
    // Reconcile the latest intent if a click or search arrived during animation.
    ["shown.bs.collapse", "hidden.bs.collapse"].forEach((eventName) => {
        children.addEventListener(eventName, (event) => {
            if (event.target === children) syncCategoryBranch(toggle);
        });
    });
    toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!expanded));
        syncCategoryBranch(toggle);
    });
});

const categorySearch = getElement("category-search");
const categoryToggles = [...root.querySelectorAll(".category-toggle")];
let categoryExpansionBeforeSearch = null;
categorySearch.addEventListener("input", () => {
    const query = categorySearch.value.trim().toLowerCase();
    if (query && categoryExpansionBeforeSearch === null) {
        categoryExpansionBeforeSearch = categoryToggles.map((toggle) => toggle.getAttribute("aria-expanded"));
    }
    const visibleItems = new Set();
    const matches = [...categoryOptions].filter((option) =>
        option.dataset.category && option.textContent.toLowerCase().includes(query));
    matches.forEach((option) => {
        const item = option.closest("li");
        visibleItems.add(item);
        item.querySelectorAll("li").forEach((child) => visibleItems.add(child));
        let parent = item.parentElement.closest("li");
        while (parent) {
            visibleItems.add(parent);
            parent = parent.parentElement.closest("li");
        }
    });
    categoryOptions.forEach((option) => {
        option.closest("li").hidden = Boolean(query) && !visibleItems.has(option.closest("li"));
    });
    root.querySelectorAll(".category-menu .dropdown-divider").forEach((divider) => {
        divider.parentElement.hidden = Boolean(query);
    });
    categoryToggles.forEach((toggle, index) => {
        const children = document.getElementById(toggle.getAttribute("aria-controls"));
        const expanded = query ? [...children.children].some((item) => !item.hidden)
            : categoryExpansionBeforeSearch?.[index] === "true";
        if (query || categoryExpansionBeforeSearch !== null) {
            toggle.setAttribute("aria-expanded", String(expanded));
            syncCategoryBranch(toggle);
        }
    });
    if (!query) categoryExpansionBeforeSearch = null;
    getElement("category-no-results").hidden = matches.length > 0;
});

});

const adminModalElement = document.getElementById("admin-modal");
const adminFields = [...(adminModalElement?.querySelectorAll("form input, form textarea, form select") || [])];
const initialAdminFields = adminFields.map((field) => ({
    field,
    value: field.value,
    checked: field.checked,
}));
function hasAdminChanges() {
    return initialAdminFields.some(({ field, value, checked }) => {
        if (field.type === "search") return false;
        return field.type === "checkbox" || field.type === "radio"
            ? field.checked !== checked : field.value !== value;
    });
}
const discardConfirmation = document.getElementById("discard-confirmation");
const keepEditingButton = document.getElementById("keep-editing");
const discardButton = document.getElementById("discard-changes");
let allowAdminDiscard = false;
let focusBeforeConfirmation = null;
let discardClosing = false;
function closeDiscardConfirmation(discard = false) {
    if (discardClosing) return;
    discardClosing = true;
    discardConfirmation.classList.remove("is-visible");
    const duration = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 200;
    window.setTimeout(() => {
        discardConfirmation.hidden = true;
        [...discardConfirmation.parentElement.children].forEach((child) => {
            if (child !== discardConfirmation) child.inert = false;
        });
        discardClosing = false;
        if (discard) {
            allowAdminDiscard = true;
            bootstrap.Modal.getOrCreateInstance(adminModalElement).hide();
        } else {
            focusBeforeConfirmation?.focus();
        }
    }, duration);
}
keepEditingButton?.addEventListener("click", () => closeDiscardConfirmation());
discardButton?.addEventListener("click", () => {
    closeDiscardConfirmation(true);
});
discardConfirmation?.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        closeDiscardConfirmation();
    } else if (event.key === "Tab") {
        event.preventDefault();
        (document.activeElement === keepEditingButton ? discardButton : keepEditingButton).focus();
    }
});
adminModalElement?.addEventListener("hide.bs.modal", (event) => {
    if (event.target !== adminModalElement) return;
    if (!addSuccess.hidden) {
        event.preventDefault();
        closeAddSuccess();
        return;
    }
    if (hasAdminChanges() && !allowAdminDiscard) {
        event.preventDefault();
        if (!discardConfirmation.hidden) return;
        focusBeforeConfirmation = document.activeElement;
        discardConfirmation.hidden = false;
        void discardConfirmation.offsetWidth;
        discardConfirmation.classList.add("is-visible");
        [...discardConfirmation.parentElement.children].forEach((child) => {
            if (child !== discardConfirmation) child.inert = true;
        });
        keepEditingButton.focus();
    }
});
adminModalElement?.addEventListener("hidden.bs.modal", (event) => {
    if (event.target !== adminModalElement) return;
    allowAdminDiscard = false;
    initialAdminFields.forEach(({ field, value, checked }) => {
        field.value = value;
        if (field.type === "checkbox" || field.type === "radio") field.checked = checked;
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.dispatchEvent(new Event("change", { bubbles: true }));
    });
    adminModalElement.querySelectorAll('[data-category=""]').forEach((option) => option.click());
    adminModalElement.querySelectorAll(".admin-form-status").forEach((status) => { status.textContent = ""; });
    adminModalElement.querySelectorAll(".category-toggle").forEach((toggle) => {
        toggle.setAttribute("aria-expanded", "false");
    });
    adminModalElement.querySelectorAll(".collapse, .collapsing").forEach((panel) => {
        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).hide();
    });
    adminModalElement.querySelectorAll('[data-bs-toggle="dropdown"]').forEach((trigger) => {
        bootstrap.Dropdown.getInstance(trigger)?.hide();
    });
});
// Finish resetting a panel even if it was still animating when the modal closed.
adminModalElement?.addEventListener("shown.bs.collapse", (event) => {
    if (!adminModalElement.classList.contains("show")) {
        bootstrap.Collapse.getOrCreateInstance(event.target, { toggle: false }).hide();
    }
});

// Let the exit animation finish before Bootstrap removes the dropdown.
document.querySelectorAll('[data-picker] [data-bs-toggle="dropdown"]').forEach((trigger) => {
    const menu = trigger.closest("[data-picker]").querySelector(".dropdown-menu");
    let closing = false;
    let finishHide = false;
    trigger.addEventListener("hide.bs.dropdown", (event) => {
        if (finishHide || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        event.preventDefault();
        if (closing) return;
        closing = true;
        menu.classList.add("is-closing");
        window.setTimeout(() => {
            finishHide = true;
            bootstrap.Dropdown.getOrCreateInstance(trigger).hide();
            menu.classList.remove("is-closing");
            closing = false;
            finishHide = false;
        }, 180);
    });
});

const addSuccess = document.getElementById("add-success");
const doneAdding = document.getElementById("close-add-success");
let successPreviousFocus = null;
let successClosing = false;
function showAddSuccess(form, saved = false) {
    document.getElementById("add-success-note").textContent = saved
        ? "Your tag has been saved." : "Preview only — no data has been saved.";
    const entity = form.getAttribute("aria-label").replace("Add ", "");
    const verb = form.dataset.mode === "edit" ? "updated" : "added";
    document.getElementById("add-success-title").textContent = `${entity[0].toUpperCase()}${entity.slice(1)} ${verb} successfully`;
    successPreviousFocus = document.activeElement;
    [...addSuccess.parentElement.children].forEach((child) => {
        if (child !== addSuccess) child.inert = true;
    });
    addSuccess.hidden = false;
    void addSuccess.offsetWidth;
    addSuccess.classList.add("is-visible");
    doneAdding.focus();
}
function closeAddSuccess() {
    if (successClosing || addSuccess.hidden) return;
    successClosing = true;
    addSuccess.classList.remove("is-visible");
    window.setTimeout(() => {
        addSuccess.hidden = true;
        [...addSuccess.parentElement.children].forEach((child) => {
            if (child !== addSuccess) child.inert = false;
        });
        successClosing = false;
        successPreviousFocus?.focus();
    }, matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 200);
}
doneAdding?.addEventListener("click", closeAddSuccess);
addSuccess?.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        closeAddSuccess();
    } else if (event.key === "Tab") {
        event.preventDefault();
        doneAdding.focus();
    }
});

 document.getElementById("clear-filters")?.addEventListener("click", () => {
    const panel = document.querySelector(".filter-panel");
    panel.querySelectorAll('input[type="search"]').forEach((input) => {
        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    panel.querySelector('[data-category=""]').click();
    panel.querySelector("#clear-tags").click();
});

// A top-layer popover escapes the scrollable modal without moving form controls.
document.querySelectorAll('#admin-modal [data-picker="category"] .dropdown-menu').forEach((menu) => {
    const trigger = menu.closest('[data-picker="category"]').querySelector('[data-bs-toggle="dropdown"]');
    if (!menu.showPopover) return;
    menu.setAttribute("popover", "manual");
    menu.classList.remove("w-100");
    menu.classList.add("category-floating-menu");
    bootstrap.Dropdown.getOrCreateInstance(trigger, { display: "static" });
    function positionMenu() {
        if (!menu.matches(":popover-open")) return;
        const rect = trigger.getBoundingClientRect();
        const below = window.innerHeight - rect.bottom - 12;
        const above = rect.top - 12;
        const openBelow = below >= Math.min(menu.scrollHeight, 280) || below >= above;
        menu.style.width = `${rect.width}px`;
        menu.style.left = `${rect.left}px`;
        menu.style.top = openBelow ? `${rect.bottom + 4}px` : "auto";
        menu.style.bottom = openBelow ? "auto" : `${window.innerHeight - rect.top + 4}px`;
        menu.style.maxHeight = `${Math.max(0, openBelow ? below : above)}px`;
    }
    trigger.addEventListener("shown.bs.dropdown", () => {
        menu.showPopover();
        positionMenu();
    });
    trigger.addEventListener("hidden.bs.dropdown", () => menu.hidePopover());
    window.addEventListener("resize", positionMenu);
    document.addEventListener("scroll", positionMenu, true);
    adminModalElement.addEventListener("hide.bs.modal", () => bootstrap.Dropdown.getInstance(trigger).hide());
});
