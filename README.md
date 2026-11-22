# Product catalog assignment

A Django product dashboard with description/name search, category filtering, and
multiple-tag filtering. Products, categories, and tags are managed through the
built-in Django admin. The dashboard header's **Admin** link opens `/admin/`.
The former custom `/manage/` page and its mutation endpoints have been removed.

## Install and run from scratch

Prerequisites:

- Python 3.12 or newer, with `pip`, `venv`, and SQLite support. The clean-install
  check used Python 3.15.2 on macOS; other Python versions/platforms were not tested.
- Git to clone the repository and internet access for the initial package install.
- Node.js is optional and only needed for JavaScript tests (verified with 26.7.0).

From a terminal on macOS or Linux:

```sh
git clone https://github.com/masoudimp/DJango.git
cd DJango
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

On Windows, create the environment with `py -m venv .venv`, and replace
`.venv/bin/python` with `.venv\Scripts\python.exe` in the remaining commands.
Windows setup has not been tested. Using the environment's Python directly avoids
requiring shell activation. To leave the development server, press Ctrl+C.

`requirements.txt` pins Django 6.1.3 and its asgiref/sqlparse dependencies to the
versions verified by a fresh package install. No npm install or frontend build
is needed: Bootstrap CSS and bundled JavaScript are served from
`products/static/products/vendor/bootstrap/`.

Open http://127.0.0.1:8000/ for the dashboard and
http://127.0.0.1:8000/admin/ for management. Follow the interactive superuser prompts
and use your chosen credentials. No default account is included in the repository.

SQLite stores local data in `db.sqlite3`, which is excluded from Git. Migration
creates the tables, not sample products or accounts; an empty dashboard on first
startup is expected. Populate records through Django admin as described below.

No environment variables or `.env` file are required for local setup. Settings in
`config/settings.py` are for local development (`DEBUG=True`, local development
secret key, SQLite). These instructions do not configure a production deployment.
If port 8000 is occupied, use `manage.py runserver 8001` and open port 8001 instead.

## Django admin and sample data

Create categories, optionally choosing a parent; create tags; then create
products with a title and category. Description and tags are optional in the
model. The product admin offers a multiple-tag selector, search, and list filters.
No image input or upload is exposed. Products without images show the supplied
placeholder. Django admin requires a staff account with appropriate permissions.

The assignment requires entering at least 5 categories, 10 tags, and 20 products
through Django admin, with varied descriptions and tag combinations.

On 2026-11-22, all **13 categories, 10 tags, and 20 products** were entered through
the actual Django admin browser forms in a fresh database. All products have
descriptions and two tags. The category hierarchy and all 40 product/tag links
were compared with the previous catalog and matched. Each of the 43 records has
an admin creation log. This verified database replaced the previous local one;
existing login accounts were preserved. IDs may differ from the old dataset.

Codex operated the browser forms with user authorization; this is not a claim
that the applicant personally typed every record. Earlier direct/custom-UI
population was superseded by this full admin-based entry. The database remains
excluded from Git, so a reproducible sample-data delivery process is still needed
for reviewers. Tests do not count as working-database sample entry.

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
Clean-install verification completed on 2026-11-22 in a separate temporary copy,
with a new virtual environment and no pre-existing database:

- Installed packages from PyPI using only `requirements.txt`; `pip check` passed.
- Applied every migration successfully; system checks passed and no migrations
  were missing.
- Passed 16 Django tests and 4 JavaScript tests.
- Started the development server and verified HTTP 200 for the dashboard, product
  filter endpoint, admin login, dashboard JavaScript, and Bootstrap CSS.

This check used the current local source snapshot, not a fresh clone of the
published repository. Commit and push these setup files before giving reviewers
the clone instructions. Desktop Chrome browser checks completed on 2026-11-22:

- Description search (`warehouse`) and case-insensitive title search (`jAcKeT`).
- Combined search/category/tags, empty results, parent/leaf categories, and ANY-tag
  matching without duplicate cards.
- Category/tag deselection and Clear restored all 20 products.
- Product details opened after filtering; Admin opened in a separate tab.
- In a separate copied database on port 8019: created and edited a category,
  tag, and product; verified product relationships and clearing its tags;
  rejected self-parenting; blocked deletion of a category containing a product.

After user confirmation, deleted the temporary product, category, and tag through
Django admin and verified their success messages. The remaining catalog in the
test database matches the original, including product/tag associations.
The original catalog was unchanged (20 products,
13 categories, 10 tags). These checks cover desktop Chrome; mobile and other
browsers were not tested.

## AI assistance

Codex generated the initial models and migrations, dashboard templates and styling,
filter DTO/query logic, JavaScript interactions, tests, Django admin integration,
and dependency/setup documentation.
Codex also built, then removed at the applicant's request, a custom CRUD panel.
The original AI-assisted sample insertion used direct database access. At the
user's request, Codex subsequently recreated the entire sample catalog through
Django admin browser forms and verified the resulting records and admin logs.

Applicant review, understanding, and significant personal contributions must be
completed and accurately documented before submission, as required by the
assignment's AI policy. Further agent-generated changes are not evidence of
personal contributions. Historical decisions are recorded in `docs/decisions.md`.
