from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class CategoryCreate:
    name: str
    color: str | None = None


@dataclass(frozen=True)
class CategoryOut:
    id: int
    name: str
    color: str | None = None
