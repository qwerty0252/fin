import uuid
from datetime import datetime, timezone

from pydantic import BaseModel as PydanticBase, ConfigDict, Field


class BaseModel(PydanticBase):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(PydanticBase):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IDMixin(PydanticBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
