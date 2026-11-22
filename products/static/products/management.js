let managementTrigger = null;

function openManagementForm(kind, row, trigger) {
    managementTrigger = trigger;
    const editing = Boolean(row);
    const action = editing ? "Edit" : "Add";

    // Keep hidden request fields while clearing the visible form.
    adminFields.forEach((field) => {
        if (["csrfmiddlewaretoken", "source"].includes(field.name)) return;
        if (field.type === "checkbox") field.checked = false;
        else field.value = "";
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.dispatchEvent(new Event("change", { bubbles: true }));
    });
    adminModalElement.querySelectorAll('[data-category=""]').forEach((option) => option.click());
    adminModalElement.querySelectorAll(".admin-form-status").forEach((status) => { status.textContent = ""; });

    document.getElementById("admin-modal-title").textContent = `${action} ${kind}`;
    const panel = document.getElementById(`add-${kind}-panel`);
    const form = panel.querySelector("form");
    form.querySelector("h3").hidden = true;
    form.querySelector('[type="submit"]').textContent = editing ? "Save changes" : `Add ${kind}`;
    form.dataset.mode = editing ? "edit" : "add";
    form.action = editing ? row.dataset.editUrl : form.dataset.createUrl;
    document.querySelectorAll("#admin-forms > .collapse").forEach((item) => {
        item.classList.toggle("show", item === panel);
    });

    if (row) {
        document.getElementById(`new-${kind}-title`).value = row.dataset.title;
        const categoryPicker = form.querySelector('[data-picker="category"]');
        categoryPicker?.querySelectorAll("[data-category]").forEach((option) => {
            if (option.dataset.category === row.dataset.category) option.click();
        });
        if (kind === "product") {
            document.getElementById("new-product-description").value = row.dataset.description;
            const tags = row.dataset.tags.split("|");
            form.querySelectorAll('.tag-options input').forEach((input) => {
                input.checked = tags.includes(input.value);
                input.dispatchEvent(new Event("change", { bubbles: true }));
            });
        }
    }
    // An untouched Edit form is not an unsaved change.
    initialAdminFields.forEach((initial) => {
        initial.value = initial.field.value;
        initial.checked = initial.field.checked;
    });
    bootstrap.Modal.getOrCreateInstance(adminModalElement).show();
}

document.querySelectorAll("[data-manage-add]").forEach((button) => {
    button.addEventListener("click", () => openManagementForm(button.dataset.manageAdd, null, button));
});
document.querySelectorAll("[data-manage-edit]").forEach((button) => {
    button.addEventListener("click", () => {
        const row = button.closest("tr");
        openManagementForm(row.dataset.kind, row, button);
    });
});
adminModalElement.addEventListener("hidden.bs.modal", () => managementTrigger?.focus());

const deletePreview = document.getElementById("delete-preview");
const deleteForm = document.getElementById("delete-form");
document.querySelectorAll("[data-manage-delete]").forEach((button) => {
    button.addEventListener("click", () => {
        managementTrigger = button;
        const deleteUrl = button.closest("tr").dataset.deleteUrl;
        deleteForm.dataset.realDelete = deleteUrl ? "true" : "false";
        deleteForm.action = deleteUrl || "";
        document.getElementById("delete-preview-text").textContent = `Do you want to delete “${button.closest("tr").dataset.title}”?`;
        document.getElementById("delete-preview-status").textContent = deleteUrl
            ? button.closest("tr").dataset.kind === "category"
                ? "Categories with subcategories or products cannot be deleted."
                : button.closest("tr").dataset.kind === "product"
                    ? "This will delete the product. Its category and tags will be kept."
                    : "This will delete the tag and remove it from any linked products."
            : "Preview only — no records will be deleted.";
        bootstrap.Modal.getOrCreateInstance(deletePreview).show();
    });
});
deleteForm.addEventListener("submit", (event) => {
    if (deleteForm.dataset.realDelete === "true") {
        document.getElementById("confirm-preview-delete").disabled = true;
        return;
    }
    event.preventDefault();
    document.getElementById("delete-preview-status").textContent = "Delete preview complete. No data was changed.";
});
deletePreview.addEventListener("hidden.bs.modal", () => managementTrigger?.focus());

const managementSuccess = document.getElementById("management-success");
if (managementSuccess) {
    bootstrap.Modal.getOrCreateInstance(managementSuccess).show();
    managementSuccess.addEventListener("hidden.bs.modal", () => {
        document.querySelector('[role="tab"][aria-selected="true"]')?.focus();
    });
}

["tag", "category", "product"].forEach((kind) => {
    const form = document.getElementById(`create-${kind}-form`);
    if (!document.getElementById(`management-${kind}-invalid`)) return;
    const editing = form.dataset.mode === "edit";
    document.getElementById("admin-modal-title").textContent = `${editing ? "Edit" : "Add"} ${kind}`;
    form.querySelector('[type="submit"]').textContent = editing ? "Save changes" : `Add ${kind}`;
    document.getElementById(`add-${kind}-panel`).classList.add("show");
    form.querySelector("h3").hidden = true;
    adminModalElement.addEventListener("shown.bs.modal", () => {
        document.getElementById(`new-${kind}-title`).focus();
    }, { once: true });
    bootstrap.Modal.getOrCreateInstance(adminModalElement).show();
});
