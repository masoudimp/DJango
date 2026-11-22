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
