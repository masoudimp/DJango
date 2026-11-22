# DJango

## Current models

The `products` app currently defines `Tag` and `Category`. Each has an automatic
integer primary key (`id`) and a required, unique `title` of up to 100 characters.
The Product model and its relationships are not implemented yet.

`AssetType` has an automatic ID and a required, unique title (up to 100 characters).
`Asset` has an automatic ID, a required, unique title (up to 200 characters), a
required URL (up to 200 characters), and a required asset type. Asset types in use
cannot be deleted. Assets store URLs only; file uploads are not implemented.

Category has an optional parent category (`parent_id` in the database); a null parent
denotes a root category. Children are accessible through `category.children`.
Deleting a category with children is protected. Self-parent and cycle validation
are deferred in the [user-requested TODO list](docs/todo.md).

## AI assistance

Codex generated the initial `Tag`, `Category`, `AssetType`, and `Asset` models,
app configuration, and migrations, added the Category parent relation, and assisted
with setup and documentation. Applicant review and personal modifications to the
generated implementation are pending.

## Database

The project uses SQLite, configured in `config/settings.py`. No separate database
server is required. Django uses `db.sqlite3` in the project root; this local database
file is excluded from Git.

With the virtual environment and Django installed, create the database tables with:

```sh
.venv/bin/python manage.py migrate
```

See [the decision log](docs/decisions.md) for the rationale (DEC-002).
