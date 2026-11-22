# DJango

## Current models

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

Codex also integrated Bootstrap and generated the shared base template.

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
`title`, `content`, `extra_css`, and `extra_js` blocks. The base template is ready;
no listing view or route has been added yet.

## Database

The project uses SQLite, configured in `config/settings.py`. No separate database
server is required. Django uses `db.sqlite3` in the project root; this local database
file is excluded from Git.

With the virtual environment and Django installed, create the database tables with:

```sh
.venv/bin/python manage.py migrate
```

See [the decision log](docs/decisions.md) for the rationale (DEC-002).
