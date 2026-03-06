from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# Collection schemas
class CollectionCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    created_at: datetime


# Bookmark schemas
class BookmarkCreate(BaseModel):
    title: str = Field(..., max_length=255)
    url: str = Field(..., max_length=2048)
    notes: Optional[str] = None


class BookmarkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=2048)
    notes: Optional[str] = None


class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    notes: Optional[str]
    created_at: datetime
    collection_id: int
