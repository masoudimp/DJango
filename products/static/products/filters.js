const filterPanel = document.querySelector(".filter-panel");
const productGrid = document.getElementById("product-grid");
const filterStatus = document.getElementById("filter-status");
const searchInput = document.getElementById("search");
let searchTimer;
let activeRequest;
let resettingFilters = false;

function readFilters() {
    const category = document.getElementById("category-value").value;
    const tags = [...filterPanel.querySelectorAll('input[name="tags"]:checked')];
    return {
        categoryId: category ? Number(category) : null,
        tagIds: tags.length ? tags.map((input) => Number(input.value)) : null,
        search: searchInput.value.trim() || null,
    };
}

async function loadProducts() {
    clearTimeout(searchTimer);
    activeRequest?.abort();
    const controller = new AbortController();
    activeRequest = controller;
    const filters = readFilters();
    const query = new URLSearchParams();
    // Omitted query parameters represent null; an empty query means get all.
    if (filters.categoryId !== null) query.set("categoryId", filters.categoryId);
    filters.tagIds?.forEach((id) => query.append("tagIds", id));
    if (filters.search !== null) query.set("search", filters.search);

    productGrid.setAttribute("aria-busy", "true");
    filterStatus.textContent = "Loading products…";
    try {
        const response = await fetch(`${productGrid.dataset.filterUrl}?${query}`, {
            signal: controller.signal,
        });
        if (!response.ok) throw new Error("Could not load products.");
        const html = await response.text();
        if (controller.signal.aborted) return;
        disposeProductCards();
        productGrid.innerHTML = html;
        disposeProductCards = initializeProductCards(productGrid);
        filterStatus.textContent = `${productGrid.querySelectorAll(".product-card").length} products found.`;
    } catch (error) {
        if (!controller.signal.aborted) {
            filterStatus.textContent = "Could not load products. Change a filter or clear filters to retry.";
        }
    } finally {
        if (activeRequest === controller) productGrid.setAttribute("aria-busy", "false");
    }
}

searchInput.addEventListener("input", () => {
    if (resettingFilters) return;
    clearTimeout(searchTimer);
    // Cancel immediately, even during the debounce delay, to avoid stale results.
    activeRequest?.abort();
    searchTimer = setTimeout(loadProducts, 300);
});
filterPanel.querySelectorAll("[data-category]").forEach((option) => {
    option.addEventListener("click", () => {
        if (!resettingFilters) loadProducts();
    });
});
filterPanel.querySelectorAll('input[name="tags"]').forEach((input) => {
    input.addEventListener("change", loadProducts);
});
document.getElementById("clear-tags").addEventListener("click", () => {
    if (!resettingFilters) loadProducts();
});
document.getElementById("clear-filters").addEventListener("click", () => {
    // Reset existing picker controls, then send exactly one request.
    resettingFilters = true;
    filterPanel.querySelectorAll('input[type="search"]').forEach((input) => {
        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    filterPanel.querySelector('[data-category=""]').click();
    document.getElementById("clear-tags").click();
    resettingFilters = false;
    loadProducts();
});
