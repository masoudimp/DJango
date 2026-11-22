# DJango

## Current models

The `products` app currently defines `Tag` and `Category`. Each has an automatic
integer primary key (`id`) and a required, unique `title` of up to 100 characters.
The Product model and its relationships are not implemented yet.

## AI assistance

Codex generated the initial `Tag` and `Category` models, app configuration, and migrations, and
assisted with setup and documentation. Applicant review and personal modifications
to the generated implementation are pending.

## Database

The project uses SQLite, configured in `config/settings.py`. No separate database
server is required. Django uses `db.sqlite3` in the project root; this local database
file is excluded from Git.

With the virtual environment and Django installed, create the database tables with:

```sh
.venv/bin/python manage.py migrate
```

See [the decision log](docs/decisions.md) for the rationale (DEC-002).
