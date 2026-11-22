# Decision Log

Record meaningful project decisions here so the applicant and future agents can understand what was chosen and why.

## Instructions for agents

- Read this log before implementation and update it when making or changing a meaningful technical decision.
- Use sequential IDs (`DEC-001`, `DEC-002`, ...), a date, and a concise title.
- Explain the problem, options considered, chosen approach, rationale, and tradeoffs.
- Distinguish employer requirements, user decisions, and agent-selected implementation choices. Do not describe an agent choice as user-approved unless the user actually approved it.
- Use `Proposed`, `Accepted`, or `Superseded` as the status. Accepted means chosen for this project; it does not imply implementation or user approval.
- Link relevant code, documentation, or tests when they exist. Describe implementation and verification separately from the decision itself.
- Preserve previous entries when decisions change; mark them superseded and link the replacement entry.
- Keep entries brief and specific. Record consequential choices such as model relationships, tag matching semantics, invalid-filter handling, database selection, and front-end approach.
- Keep the README consistent with decisions that affect setup or application behavior.

## Decisions

### DEC-001: Use Django's MTV architecture

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Context:** Choose an application structure appropriate for this Django assignment and the applicant's introduction to Django.

**Options considered:** Django's conventional Model–Template–View (MTV) structure; a layered Data/Business/Controller structure; strict Clean Architecture with independent domain entities and repository contracts.

**Decision:** Use Django's conventional MTV architecture. Models define data and relationships through Django ORM, templates render HTML, and views handle HTTP requests and responses with URL routing. Organize related functionality into Django apps. A service module may be added if business logic warrants it; it is not required by this decision.

**Rationale:** MTV aligns with the assignment's emphasis on Django models, querysets, views, and a simple HTML interface. It keeps the project approachable and appropriately scoped for a short take-home exercise.

**Tradeoffs:** Models depend on Django ORM, so the domain is not independent of the framework. This avoids the additional entities, mappings, and repository abstractions of strict Clean Architecture.

**Implementation / verification:** Decision recorded; feature implementation is pending. No application code was changed as part of this entry.

**Supersedes / superseded by:** None.

### DEC-002: Use SQLite

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Context:** Select the database for the take-home project. The assignment does not require a specific database engine.

**Options considered:** SQLite, or a separate database server such as PostgreSQL.

**Decision:** Use SQLite through Django ORM, with the database file at `BASE_DIR / 'db.sqlite3'`.

**Rationale:** SQLite keeps local setup simple and requires no separate database server, which fits this small assignment.

**Tradeoffs:** SQLite offers less write concurrency than a server-based database; this is acceptable for the intended local demonstration.

**Implementation / verification:** Confirmed that [settings.py](../config/settings.py) already configures `django.db.backends.sqlite3`. No settings change was needed. `manage.py check` passed. Database migrations and sample-data population were not performed as part of this decision.

**Supersedes / superseded by:** None.

### DEC-003: Define Tag with an ID and title

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (fields); Agent (app placement and field constraints)

**Context:** Implement the tag model first, with only `id` and `title`.

**Options considered:** An explicit ID versus Django's automatic primary key; a plain title versus a unique title.

**Decision:** Define `Tag` in the `products` app, inheriting directly from `models.Model`. Use an automatic `BigAutoField` ID and a required `CharField` title with `max_length=100` and `unique=True`. Return the title from `__str__`.

**Rationale:** Keeps the model simple and prevents duplicate titles while giving it a readable display name. No custom base model is needed.

**Tradeoffs:** The title length and uniqueness are implementation choices, not employer requirements. Uniqueness does not enforce case-insensitive matching; case variants may coexist.

**Implementation / verification:** Added the model, registered its app, and generated `0001_initial.py`. Django's system check passed. The migration has not been applied; product relationships and admin registration remain pending.

**Supersedes / superseded by:** None.

### DEC-004: Define Category consistently with Tag

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (add categories); Agent (field choices)

**Context:** Add categories as the next model in the incremental implementation.

**Options considered:** A minimal title-based model matching Tag, or additional fields and a category hierarchy.

**Decision:** Define `Category` in the `products` app with an automatic `BigAutoField` ID and a required, unique title of up to 100 characters. Return the title from `__str__` and set the plural display name to `categories`.

**Rationale:** Matches the existing Tag model and keeps the implementation within the assignment's scope.

**Tradeoffs:** Title constraints are implementation assumptions, not employer requirements. Case variants may coexist; no category hierarchy is provided.

**Implementation / verification:** Generated `0002_category.py`. Django's system check passed and the migration consistency check reported no changes. This migration has not been applied. Product relationships and admin registration remain pending.

**Supersedes / superseded by:** None.

### DEC-005: Add an optional parent to Category

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (hierarchy and deferred validation); Agent (PROTECT deletion behavior)

**Context:** The user requested parent/child categories using a nullable parent ID, with hierarchy validation deferred to user-requested TODOs.

**Options considered:** Flat categories, or a self-referencing foreign key.

**Decision:** Add a self-referencing `parent` foreign key with `null=True`, `blank=True`, and `related_name="children"`. Use `PROTECT` to prevent deletion of a parent that still has children. Keep the existing title constraints.

**Rationale:** Root categories have no parent; other categories reference their parent through the generated `parent_id` column. Protection avoids accidental deletion of child categories.

**Tradeoffs:** A parent with children cannot be deleted until those relationships are removed or reassigned. Self-parent and cycle prevention are intentionally deferred in [the TODO list](todo.md), so the current model does not guarantee an acyclic hierarchy. This optional feature does not conflict with the assignment.

**Implementation / verification:** Added the field and generated `0003_category_parent.py`; migration was not applied. Django system and migration consistency checks passed.

**Supersedes / superseded by:** Replaces the flat-category aspect of DEC-004; its other decisions remain unchanged.

### DEC-006: Store assets by URL with unique titles

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (models and unique titles); Agent (PROTECT deletion behavior)

**Context:** Add assets and asset types before implementing Product, using the proposed fields and the user's requirement that asset titles be unique.

**Options considered:** URL references versus uploaded files; unique versus non-unique asset titles.

**Decision:** Define `AssetType` with an automatic ID and a required, unique title of up to 100 characters. Define `Asset` with an automatic ID, a required, unique title of up to 200 characters, a required `URLField` (default limit: 200 characters), and a required foreign key to `AssetType`. Use `PROTECT` for deletion and `assets` for reverse access.

**Rationale:** Implements the agreed URL-based structure and avoids deleting a type that is still referenced by assets.

**Tradeoffs:** Files are not uploaded or stored by the application. Titles are globally unique within each model, but case variants may coexist. These models are optional additions to the assignment. No Product model or relationship is introduced.

**Implementation / verification:** Generated `0004_assettype_asset.py` without applying it. Django system and migration consistency checks passed. No TODO items were added.

**Supersedes / superseded by:** None.

### DEC-007: Define Product with Django-managed tags

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (required/nullable fields and automatic join table); Agent (field length and deletion behavior)

**Context:** Implement Product after agreeing on its fields and changing the earlier preference for a custom ProductTag model to Django's automatic many-to-many table.

**Options considered:** An explicit ProductTag model versus a Django-managed join table.

**Decision:** Use an automatic ID, a required non-unique title (200 characters), a nullable/optional description, a required Category foreign key with `PROTECT`, an optional Asset image foreign key with `SET_NULL`, and an optional `ManyToManyField` to Tag. Django manages the join table with its own ID and unique product/tag pairs.

**Rationale:** Matches the user's field requirements and delegates standard relationship management to Django.

**Tradeoffs:** Descriptions may be NULL or empty. Image references are not restricted by asset type. The automatic join table has no custom metadata. Category deletion is blocked while referenced; image deletion preserves the product.

**Implementation / verification:** Generated `0005_product.py` without applying it. Django system and migration consistency checks passed. Inspected generated SQL to confirm field nullability and the separate `products_product_tags` table with an ID and unique product/tag pairs. No TODO items added.

**Supersedes / superseded by:** Replaces the earlier conversational preference for a custom ProductTag model.

### DEC-008: Use locally bundled Bootstrap for Django templates

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (Bootstrap); Agent (local assets and base template)

**Context:** Prepare Bootstrap for future views without implementing application pages yet.

**Options considered:** CDN inclusion, local compiled assets, or an npm build pipeline.

**Decision:** Use Bootstrap 5.3.9, the current stable release identified in the official Bootstrap documentation and blog. Store compiled CSS, bundled JavaScript including Popper, and the license locally. Provide `products/base.html` with reusable template blocks.

**Rationale:** Local assets avoid runtime CDN dependencies and require no front-end build tooling for this small Django assignment.

**Tradeoffs:** Dependency updates require replacing the bundled files. No custom styling, listing view, or route is introduced.

**Implementation / verification:** Downloaded version-pinned files from jsDelivr. Django's system check passed; rendering the base template and resolving both static assets succeeded. No browser UI verification was performed because no page route exists yet. No TODO items added.

**Supersedes / superseded by:** None.

### DEC-009: Add a static dashboard and product image fallback

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (static dashboard, asset folder, and supplied fallback image); Agent (layout and reusable card template)

**Context:** Preview the catalog interface before connecting it to database records.

**Options considered:** Database-backed cards versus fixed demonstration content; inline image handling versus a reusable card template.

**Decision:** Serve a Bootstrap dashboard at `/` with static statistics and six sample products. Keep search/filter controls disabled and label the page as a preview. Move the supplied image to `products/static/products/assets/images/image-not-available.jpg`. Use a shared card template that selects the placeholder when the image relation or URL is empty, and the asset URL otherwise.

**Rationale:** Provides the requested interface without introducing database population or query behavior. The fallback also supports real Product instances later.

**Tradeoffs:** Statistics are illustrative and filters are not functional yet; this is an intermediate step, not completion of the assignment's search/filter requirements. The fallback covers absent URLs, not remote download failures.

**Implementation / verification:** Django system check passed. Verified HTTP 200 and zero database queries for the dashboard, six fallback images, and template behavior with null, blank, and populated image URLs. Browser preview was unavailable, so visual QA could not be completed. No migrations or TODO items were added.

**Supersedes / superseded by:** None.

### DEC-010: Create tags using a simple Django form POST

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (real tag creation and beginner-friendly code); Agent (ModelForm and normal POST/redirect)

**Context:** Connect the existing Add tag UI to persistence while keeping code easy to follow.

**Options considered:** AJAX submission or a normal Django form submission.

**Decision:** Use TagForm, a POST-only view, Django CSRF and messages, and redirect after saving. Re-render invalid submissions with the entered title and errors. Use existing database uniqueness and handle concurrent duplicate writes. Tag pickers load database titles after reload; other creation forms remain previews.

**Rationale:** Standard Django form handling minimizes custom JavaScript and retains the established success modal.

**Tradeoffs:** Full-page submission does not preserve unsaved entries in other preview forms. This local demo does not yet enforce authentication. The user was reminded before implementation that custom creation does not replace the employer's required Django-admin sample population.

**Implementation / verification:** Applied existing migrations. Five Django tests passed for saving, invalid titles, duplicate titles, method restriction, and CSRF. JavaScript syntax passed. No sample tags were inserted into the working database; tests used an isolated test database. No TODOs added.

**Supersedes / superseded by:** Tag creation is now real; category/product creation remain static. DEC-009's zero-query dashboard is superseded by loading saved tags.

### DEC-011: Add a separate management UI preview

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Context:** Replace the header's Admin modal entry point with a management page featuring Products, Categories, and Tags tables.

**Options considered:** Continue using the modal as the main navigation, or use a separate page with per-section tables and form modals.

**Decision:** Add `/manage/` with static sample tables. Add opens the corresponding form, Edit prefills it from the sample row, and Delete opens a confirmation preview. Reuse the existing header, form modal, category/tag pickers, and discard behavior. All operations on this new page are UI-only, including Add tag; the existing tag backend is preserved but not called from this page.

**Rationale:** Gives each entity a clear management section while honoring the user's explicit UI-only scope.

**Tradeoffs:** Preview submissions do not change table rows or persisted data. Real CRUD and Django-admin sample population are not completed by this UI. No authentication is introduced for the static preview.

**Implementation / verification:** Django checks and five existing tag tests passed; JavaScript syntax and whitespace checks passed. Verified the management page returns HTTP 200 with zero database queries, three static forms without POST actions, unique IDs, and valid modal targets. Browser access was unavailable and native Chrome access was not approved, so visual interaction testing could not be completed. No TODOs added.

**Supersedes / superseded by:** Replaces the header Admin button's modal-opening behavior. DEC-010's tag persistence implementation remains in place.

### DEC-012: Delete database tags after confirmation

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User (deletion); Agent (normal form POST)

**Context:** Make deletion functional for the database-backed Tags table.

**Decision:** Submit a CSRF-protected POST after confirmation, find the tag by ID, delete it, and redirect to the Tags tab with a success message. Keep product/category deletion as preview actions because their rows are static samples.

**Options considered:** Fetch-based deletion or standard Django POST/redirect.

**Rationale:** A normal form submission keeps the implementation short and beginner-friendly.

**Tradeoffs:** Deletion removes product/tag associations but preserves products. The local demo still has no authentication requirement. Missing tags return 404.

**Implementation / verification:** All nine Django tests passed, including deletion, method restrictions, CSRF, missing records, and preservation of related products/other tags. No working-database records were deleted. No TODOs added.

**Supersedes / superseded by:** Replaces DEC-011's preview-only deletion for tags only.

### DEC-013: Connect management Add tag to the existing backend

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Reuse TagForm and the existing POST endpoint for management Add tag. A fixed source field returns successful requests to the Tags table and success modal. Invalid requests reopen the form with validation errors and the entered title. Preserve CSRF fields when resetting the modal.

**Rationale / tradeoffs:** Standard POST keeps the code simple. Tag editing and product/category actions remain previews.

**Implementation / verification:** Eleven Django tests pass, including management creation and duplicate validation. JavaScript syntax check passed. No TODOs added.

### DEC-014: Remove only the legacy dashboard Admin modal

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Following the user's clarification, keep the header Admin button linking to `/manage/` and remove only the old dashboard modal. Keep management table forms at `/manage/`. Tag creation now returns only to management, including validation errors. Shared JavaScript supports dashboard pages without management controls.

**Verification:** Django tests and JavaScript syntax checked. No TODO entries added.

### DEC-015: Save tag edits from management

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Reuse TagForm with the existing tag instance and shared modal. Submit edits to a POST-only endpoint; return validation errors to the same edit form and successful edits to the Tags table with a success modal.

**Rationale / tradeoffs:** Keeps the implementation simple and preserves product associations. Existing local-demo authentication limitations remain unchanged. Product/category actions remain previews.

**Implementation / verification:** All 15 Django tests passed, covering edits, validation, unchanged titles, product associations, missing records, POST restrictions, and CSRF. JavaScript syntax check passed. No TODOs added.

### DEC-016: Enable Django admin for assignment models

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: Employer requirement; user requested implementation

**Decision:** Register Product, Category, and Tag with Django admin. Reuse their
ModelForms so category cycle validation applies to both admin and custom forms.
Expose product title, description, category, and tags, with tag selection,
list search, and filters. Preserve the user's removal of image inputs.

**Rationale / tradeoffs:** Use Django's existing staff permissions and admin UI
without changing the custom management page. No working-data mutations or account
creation are needed to register models. The user must create a superuser interactively.
Existing direct/custom-UI data entry does not satisfy admin-based population.

**Implementation / verification:** Added products/admin.py and admin integration
tests for pages, related-data creation/editing, cycle rejection, and staff access.
All 39 Django tests passed; system checks passed; no migration changes detected.
README documents admin setup and remaining sample-entry requirements.

### DEC-017: Replace custom management with Django admin

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Point the header Admin link to `admin:index`. Remove `/manage/`,
custom create/edit/delete endpoints, management templates/JavaScript, and related
modal styles. Retain the dashboard, filtering, models, migrations, and existing data.
Use Django's generated Product/Tag forms; retain CategoryForm for cycle validation.

**Rationale / tradeoffs:** Django admin already provides the assignment's data
management functionality and staff permissions. Old custom CRUD URLs now return
404. Historical custom-UI tests are replaced by admin/navigation tests; filtering
tests remain. README now describes the current application instead of previews.

**Implementation / verification:** Django tests cover admin CRUD, protected deletion,
category cycles, removed routes, dashboard navigation, and filters. No working
records or accounts are changed. Admin sample entry remains outstanding.

**Supersedes:** DEC-011 through DEC-015's custom management UI and CRUD choices;
DEC-016's registration remains active, with the redundant forms removed.

### DEC-018: Fill missing sample product descriptions

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Add English sample catalog descriptions to the 19 products with
blank descriptions, preserving the existing description. Copy is based on the
supplied product names, not verified manufacturer specifications.

**Assignment conflict / warning:** Before updating, the user was informed that
direct database updates do not replace the required Django-admin data entry.
Admin entry remains the compliant workflow for fulfilling that requirement.

**Verification:** Updated inside one transaction; verified all 20 products have
nonblank descriptions and the existing description is unchanged. No schema changes.

### DEC-019: Recreate only one product through Django admin

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User explicitly limited replacement to one record

**Decision:** After backing up the catalog, delete Flame Resistant Safety Jacket
(ID 20) and recreate it through the actual Django admin browser forms as ID 21.
Preserve its description, Safety Equipment category, and Fire Resistant and
Industrial Grade tags. Do not recreate other records.

**Verification:** Browser showed deletion and creation success. Read-only checks
confirmed an admin addition log, 20 total products, and identical catalog content
against the pre-operation backup (ignoring product primary keys). This demonstrates
one admin entry, not completion of the full admin-population requirement.

### DEC-020: Pin dependencies and verify a clean local installation

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User

**Decision:** Add requirements.txt with Django 6.1.3, asgiref 3.13.0, and sqlparse
0.6.1, matching the working environment. Document clone, venv, installation,
migrations, superuser creation, server startup, configuration, and verification.

**Verification:** Copied the current local source to a temporary directory excluding
.git, .venv, and db.sqlite3. Created a new venv with Python 3.15.2 and downloaded
packages from PyPI without cache. pip check, all migrations, Django system checks,
and migration consistency checks passed. All 16 Django tests and 4 JavaScript tests
passed. Started the isolated server on port 8018; dashboard, filter fragment,
admin login, dashboard JS, and Bootstrap CSS returned HTTP 200. The working
catalog database was not changed. This is not a published-repository clone test;
Windows/other Python versions and full visual verification remain untested.

### DEC-021: Verify dashboard and admin in desktop Chrome

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User requested manual browser verification

**Decision:** Exercise the actual browser interface. Use the original dashboard
for read-only filter checks and a copied project/database on port 8019 for
admin mutations. Obtain confirmation before deleting the temporary test records.

**Verification:** Description/name search, combined filters, empty results,
parent/leaf categories, ANY-tag matching without duplicates, deselection, Clear,
filtered product details, and Admin opening in a separate tab passed. Created
and edited a temporary category, tag, and product. Verified tag clearing,
self-parent validation, and protected category deletion. After confirmation,
deleted all three temporary records through admin; success messages and restored
counts were observed. Compared all catalog rows and product/tag associations
between the copied and original databases: identical after cleanup. Original
20 products, 13 categories, and 10 tags were untouched. No functional fix was
required. Coverage is desktop Chrome, not mobile or other browsers.

### DEC-022: Populate the full sample catalog through Django admin

- Date: 2026-11-22
- Status: Accepted
- Source / decision maker: User requested completing the admin-entry requirement

**Decision:** Preserve the old database and populate a fresh migrated database
through the actual Django admin browser UI: 13 categories with parent relationships,
10 tags, and 20 products with descriptions and two tags each. Only existing login
accounts/permissions/sessions were copied for access; no catalog records were
seeded into the fresh database. Codex operated the forms on the user's behalf.

**Verification:** Browser Save/Add-another submissions created all 43 records.
Read-only comparison confirmed identical category ancestry, tag names, product
names/descriptions/categories, and 40 product/tag links against the old catalog.
Every record has a corresponding admin ADDITION log (13/10/20). After verifying
the live catalog had not changed, switched the working database to this verified
copy. SQLite integrity and foreign-key checks passed. Existing users and their
permissions were preserved. Record IDs may change. Original database snapshots
remain at /private/tmp/django-admin-entry-ckfbz2jh/original.sqlite3 and
/private/tmp/django-admin-entry-ckfbz2jh/before-switch.sqlite3 (local only; not committed).

**Supersedes:** DEC-018/019's incomplete admin-population status. Full admin-based
sample entry is now complete; reviewer data delivery is a separate remaining task.
This does not certify applicant personal contributions under the AI policy.

## Entry template

Copy this template into the Decisions section for each new entry:

```markdown
### DEC-XXX: Title

- Date: YYYY-MM-DD
- Status: Proposed | Accepted | Superseded
- Source / decision maker: Employer requirement | User | Agent

**Context:** What problem or ambiguity needs a decision?

**Options considered:** What reasonable alternatives were considered?

**Decision:** What approach was selected?

**Rationale:** Why does this approach fit the assignment?

**Tradeoffs:** What limitations or consequences does it introduce?

**Implementation / verification:** Pending, or links to relevant files and actual verification results.

**Supersedes / superseded by:** Related decision ID, if applicable.
```
