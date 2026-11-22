# Product catalog assignment

A Django product dashboard with description/name search, category filtering, and
multiple-tag filtering. Products, categories, and tags are managed through the
built-in Django admin. The dashboard header's **Admin** link opens `/admin/`.
The former custom `/manage/` page and its mutation endpoints have been removed.

## Quick start

Install Python 3.12 or newer, then clone and run:

```sh
git clone https://github.com/masoudimp/DJango.git
cd DJango
python3 run.py
```

On Windows, use `py run.py`. The launcher creates `.venv`, installs the pinned
requirements, applies migrations, and starts the server. No manual environment
activation, database configuration, or account creation is needed. Internet is
required for the first dependency installation. Python needs `venv`, `pip`, and
SQLite support. Python 3.15.2 on macOS was used for verification; Windows has not
been tested.

- Dashboard: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/
- Demo username: `admin`
- Demo password: `admin`

The included `db.sqlite3` contains 20 products, 13 categories, 10 tags, and the
assignment-only demo admin account. This database is intentionally included for
reviewer convenience. Changes made in the app are saved to this local database.
The shared demo credentials are for this local assignment, not a production account.
No `.env` file, npm installation, or frontend build is needed; Bootstrap is bundled.

Stop the server with Ctrl+C. If port 8000 is occupied:

```sh
python3 run.py --port 8001
```

The launcher uses the same environment and data on subsequent runs. Settings in
`config/settings.py` target local development (`DEBUG=True`, SQLite, local secret
key); the server binds to `127.0.0.1` only.

## Manual setup (optional)

If you prefer running each step yourself on macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

On Windows use `py -m venv .venv` and `.venv\Scripts\python.exe` instead of
`.venv/bin/python`. If starting without the included database, migrations create
empty tables; use `manage.py createsuperuser` to create an account, then enter
sample records through Django admin.

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
population was superseded by this full admin-based entry. The populated SQLite database and local demo account are included for reviewer
convenience at the user's explicit request. Tests do not count as working-database sample entry.

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

The `python3 run.py --port 8021` quick-start path was also verified in a fresh
local copy without a virtual environment, using the included populated database.
It installed dependencies and started successfully; the dashboard showed 20
products, search worked, and the demo admin credentials authenticated.


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
dependency/setup documentation, and the one-command launcher.
Codex also built, then removed at the applicant's request, a custom CRUD panel.
The original AI-assisted sample insertion used direct database access. At the
user's request, Codex subsequently recreated the entire sample catalog through
Django admin browser forms and verified the resulting records and admin logs.

Applicant review, understanding, and significant personal contributions must be
completed and accurately documented before submission, as required by the
assignment's AI policy. Further agent-generated changes are not evidence of
personal contributions. Historical decisions are recorded in `docs/decisions.md`.
