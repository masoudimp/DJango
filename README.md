# Product catalog assignment

A Django product dashboard with description/name search, category filtering, and
multiple-tag filtering. Products, categories, and tags are managed through the
built-in Django admin. The dashboard header's **Admin** link opens `/admin/`.
The former custom `/manage/` page and its mutation endpoints have been removed.

## Run locally

The existing environment uses Python 3.15.2 and Django 6.1.3. With Python and
Django installed in the project's virtual environment:

```sh
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/ for the dashboard and
http://127.0.0.1:8000/admin/ for management. Create your administrator account
interactively; do not commit credentials. SQLite stores local data in
`db.sqlite3`, which is excluded from Git. A fresh database starts empty.
Dependency installation/packaging and a clean-environment setup check remain
outstanding before submission.

Bootstrap CSS and bundled JavaScript are served locally from
`products/static/products/vendor/bootstrap/`. No frontend build is needed.

## Django admin and sample data

Create categories, optionally choosing a parent; create tags; then create
products with a title and category. Description and tags are optional in the
model. The product admin offers a multiple-tag selector, search, and list filters.
No image input or upload is exposed. Products without images show the supplied
placeholder. Django admin requires a staff account with appropriate permissions.

The assignment requires entering at least 5 categories, 10 tags, and 20 products
through Django admin, with varied descriptions and tag combinations. Existing
sample records were entered using the former custom UI/direct database operations;
this does not satisfy the admin-entry requirement. Admin-based entry and a
reproducible sample-data delivery process remain outstanding. Tests do not count
as working-database sample entry.

## Models and validation

- A product belongs to one category and may have multiple tags.
- Category and tag titles are unique; product titles need not be unique.
- Categories may have a parent. The category admin form rejects self-parenting
  and hierarchy cycles; direct ORM writes do not run this form validation.
- Categories with products or children are protected from deletion.
- Deleting a product preserves its category and tags. Deleting a tag removes
  its product associations, not the products.
- Existing Asset and AssetType models store asset URLs. The optional product
  image relation is retained; deleting an asset clears its product references.

## Dashboard filters

`ProductFilterRequest` in `products/dtos.py` accepts nullable `categoryId`,
`tagIds`, and `search`. The GET endpoint is `/products/filter/`, for example:
`/products/filter/?categoryId=1&tagIds=2&tagIds=3&search=indoor`.
Omitted or empty values mean no filter. Malformed IDs return HTTP 400.

`products/filters.py` builds a queryset:

- Category includes the selected category and its descendants.
- Tags match **any** selected tag; duplicate products are removed.
- Search performs case-insensitive contains matching on title or description.
- Different filters combine with AND; no filters returns all products.

Related category/image data is joined and tags are prefetched. The browser
waits 300 ms after typing, sends category/tag changes immediately, cancels stale
requests, and replaces only the product cards. Clear resets all filters and
sends one request. Filter selections are not persisted across page reloads.

## Verification

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test
node --test products/js_tests/filters.test.cjs
```

Node is only needed for JavaScript tests. Django tests use an isolated database.
Tests cover filter combinations, DTO parsing, admin entry/editing and permissions,
category cycle validation, deletion protection, and dashboard navigation.
JavaScript tests cover debounce, clearing, cancellation, and request failures.
Visual browser verification and a fresh-environment setup check remain outstanding.

## AI assistance

Codex generated the initial models and migrations, dashboard templates and styling,
filter DTO/query logic, JavaScript interactions, tests, and Django admin integration.
Codex also built, then removed at the applicant's request, a custom CRUD panel.
AI-assisted sample insertion used direct database access rather than Django admin.

Applicant review, understanding, and significant personal contributions must be
completed and accurately documented before submission, as required by the
assignment's AI policy. Further agent-generated changes are not evidence of
personal contributions. Historical decisions are recorded in `docs/decisions.md`.
