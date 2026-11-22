document.documentElement.dataset.inputMode = "pointer";
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
function initializeProductCards(root) {
    const observers = [];
    const tooltips = [];
root.querySelectorAll(".product-card").forEach((card) => {
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
root.querySelectorAll(".badge-rail").forEach((rail) => {
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
    const observer = new ResizeObserver(update);
    observer.observe(rail);
    observers.push(observer);
    update();
});
root.querySelectorAll('.product-description[data-bs-toggle="tooltip"]').forEach((element) => {
    tooltips.push(new bootstrap.Tooltip(element, {
        container: "body",
        trigger: "hover focus",
        customClass: "product-description-tooltip",
        html: false,
    }));
});
    return () => {
        observers.forEach((observer) => observer.disconnect());
        tooltips.forEach((tooltip) => tooltip.dispose());
    };
}
let disposeProductCards = initializeProductCards(document);
productModalElement?.addEventListener("hidden.bs.modal", () => activeProductCard?.focus({ preventScroll: true }));

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
        : selected.length === 1 ? selected[0].dataset.label : `${selected.length} tags selected`;
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
        const visible = input.dataset.label.toLowerCase().includes(query);
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
        // Clicking the selected dashboard category again clears that filter.
        const deselect = root.closest(".filter-panel") && option.dataset.category
            && getElement("category-value").value === option.dataset.category;
        const selected = deselect ? root.querySelector('[data-category=""]') : option;
        getElement("category-summary").textContent = selected.textContent;
        getElement("category-value").value = selected.dataset.category;
        categoryOptions.forEach((item) => {
            item.classList.remove("active");
            item.removeAttribute("aria-current");
        });
        selected.classList.add("active");
        selected.setAttribute("aria-current", "true");
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
