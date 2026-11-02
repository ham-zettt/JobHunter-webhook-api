from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class KeywordCreate(BaseModel):
    type: str
    term: str = Field(min_length=1)
    strength: str | None = None
    scope: str = "both"
    role_category: str | None = None
    is_regex: bool = False
    is_active: bool = True

    @model_validator(mode="after")
    def _validate(self) -> KeywordCreate:
        if self.type not in ("include", "exclude", "search_term"):
            raise ValueError("type harus include, exclude, atau search_term")
        if self.scope not in ("title", "description", "both"):
            raise ValueError("scope harus title, description, atau both")
        if self.type == "include" and self.strength not in ("strong", "weak"):
            raise ValueError("include wajib punya strength strong/weak")
        if self.type != "include" and self.strength is not None:
            raise ValueError("strength hanya untuk type include")
        self.term = self.term.strip().lower()
        return self

    def to_row(self) -> dict:
        return {
            "type": self.type,
            "term": self.term,
            "strength": self.strength,
            "scope": self.scope,
            "role_category": self.role_category,
            "is_regex": int(self.is_regex),
            "is_active": int(self.is_active),
        }


class KeywordUpdate(BaseModel):
    term: str | None = Field(default=None, min_length=1)
    strength: str | None = None
    scope: str | None = None
    role_category: str | None = None
    is_regex: bool | None = None
    is_active: bool | None = None

    def to_row(self) -> dict:
        data = self.model_dump(exclude_none=True)
        if "term" in data:
            data["term"] = data["term"].strip().lower()
        for key in ("is_regex", "is_active"):
            if key in data:
                data[key] = int(data[key])
        return data
