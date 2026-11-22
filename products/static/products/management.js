let managementTrigger = null;

function openManagementForm(kind, row, trigger) {
    managementTrigger = trigger;
    const editing = Boolean(row);
    const action = editing ? "Edit" : "Add";

    // These forms only preview changes; they never send a request.
    adminFields.forEach((field) => {
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
            ? "This will delete the tag and remove it from any linked products."
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
