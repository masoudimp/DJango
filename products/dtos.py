from dataclasses import dataclass


@dataclass
class ProductFilterRequest:
    categoryId: int | None = None
    tagIds: list[int] | None = None
    search: str | None = None

    @classmethod
    def from_query(cls, query):
        # GET lists are sent as repeated keys: ?tagIds=1&tagIds=2
        category = query.get("categoryId", "").strip()
        tags = [value for value in query.getlist("tagIds") if value.strip()]
        dto = cls(
            categoryId=int(category) if category else None,
            tagIds=list(dict.fromkeys(int(value) for value in tags)) or None,
            search=query.get("search", "").strip() or None,
        )
        ids = ([dto.categoryId] if dto.categoryId is not None else []) + (dto.tagIds or [])
        if any(value <= 0 or value > 9223372036854775807 for value in ids):
            raise ValueError("IDs must be positive integers.")
        return dto
