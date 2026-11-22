# DJango

## Current models

### Create a tag

The existing `/tags/create/` endpoint and original tag form save to SQLite using a normal Django POST
and redirects back with a success message. Empty, whitespace-only, overlong (more
than 100 characters), and duplicate titles are rejected. Titles are trimmed; the
existing database uniqueness rule is case-sensitive on SQLite.

The tag pickers load saved tags after the page reloads. Category and product
creation remain static previews. Submitting the tag form reloads the whole page,
so unfinished entries in other preview forms are not retained. This local demo
endpoint uses CSRF protection but does not yet require login.

### Management UI preview

Open `/manage/` directly. Choose Products, Categories,
or Tags to see tables with row-level Edit/Delete buttons and an Add button.
Tags are read from SQLite, ordered by title; an empty table shows “No tags found.”
Products and categories still use sample rows.
Add opens the relevant form in a modal; Edit opens it prefilled with the sample row.
Delete opens a confirmation dialog. For tags, confirming submits a CSRF-protected
POST, deletes the tag and its product associations, and returns to the Tags tab
with a success message. Products and other tags are preserved. Missing tags return
404 and GET requests cannot delete. Like creation, this local-demo endpoint does
not yet require login.

Add tag saves through the existing POST endpoint, returns to the Tags table, and
shows a success modal. Invalid titles reopen the form with the entered value and
validation error. Product/category actions and tag editing remain previews.
No real tags were deleted during development checks; tests use a separate database.

The existing category/tag pickers, modal artwork, discard confirmation, and header
are reused. Codex connected the management Add tag form to the existing backend. `/admin/` remains
the separate built-in Django admin URL.

The assignment still requires sample data to be entered through Django admin;
this custom form does not replace that requirement. No sample data was populated.

Run the focused tests with `.venv/bin/python manage.py test products`.

The `products` app currently defines `Tag` and `Category`. Each has an automatic
integer primary key (`id`) and a required, unique `title` of up to 100 characters.
`Product` has an automatic ID, a required title (up to 200 characters, not unique),
a nullable description, a required category, and an optional image referencing
`Asset`. Categories referenced by products are protected from deletion; deleting
an image asset clears the product's image reference. Image references are not yet
restricted to a particular asset type.

Products may have zero or more tags. Django manages the separate join table,
including its ID and unique product/tag pairs, through `ManyToManyField`.

`AssetType` has an automatic ID and a required, unique title (up to 100 characters).
`Asset` has an automatic ID, a required, unique title (up to 200 characters), a
required URL (up to 200 characters), and a required asset type. Asset types in use
cannot be deleted. Assets store URLs only; file uploads are not implemented.

Category has an optional parent category (`parent_id` in the database); a null parent
denotes a root category. Children are accessible through `category.children`.
Deleting a category with children is protected. Self-parent and cycle validation
are deferred in the [user-requested TODO list](docs/todo.md).

## AI assistance

Codex also integrated Bootstrap and generated the shared base template, static
dashboard view and templates, styling, and product image fallback.
Codex implemented the tag ModelForm, POST view, template integration, and tests.
Codex also created the management UI preview and extracted the shared header and
form modal templates.
Codex implemented tag deletion, its confirmation-form integration, and tests.

Codex generated the initial `Tag`, `Category`, `AssetType`, `Asset`, and `Product` models,
app configuration, and migrations, added the Category parent relation, and assisted
with setup and documentation. Applicant review and personal modifications to the
generated implementation are pending.

## Bootstrap and templates

Bootstrap 5.3.9 compiled CSS and bundled JavaScript (including Popper) are stored
locally under `products/static/products/vendor/bootstrap/`, with their license.
Source: https://cdn.jsdelivr.net/npm/bootstrap@5.3.9/.
No npm installation, front-end build, or runtime CDN access is required.

New templates can use `{% extends "products/base.html" %}` and override the
`title`, `content`, `extra_css`, and `extra_js` blocks.

Run `.venv/bin/python manage.py runserver` and open http://127.0.0.1:8000/ for the
dashboard. The six product cards are static demo content, not database
records. Category options remain static; tag options come from SQLite and support
clearing selections. Both panels use Bootstrap Collapse to expand inline in the sidebar and include case-insensitive
search over their sample options. Category search reveals matching branches and
their ancestors; clearing the search restores previous expansion states. Tag
search preserves existing selections. These selections do not filter the
cards yet, and the search input remains disabled. The dashboard queries saved tags.

The supplied placeholder image was moved to
`products/static/products/assets/images/image-not-available.jpg`. The reusable
`products/includes/product_card.html` template displays it when `product.image`
or its URL is absent/empty; otherwise it displays `product.image.url`.

## Database

The project uses SQLite, configured in `config/settings.py`. No separate database
server is required. Django uses `db.sqlite3` in the project root; this local database
file is excluded from Git.

With the virtual environment and Django installed, create the database tables with:

```sh
.venv/bin/python manage.py migrate
```

See [the decision log](docs/decisions.md) for the rationale (DEC-002).

The header Admin button opens `/manage/`; only the legacy dashboard Admin modal has been removed.
Management forms remain available on `/manage/`; tag submissions return there.
