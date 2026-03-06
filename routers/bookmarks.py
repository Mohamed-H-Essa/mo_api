from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from database import get_db
from models import Collection, Bookmark
from schemas import BookmarkCreate, BookmarkUpdate, BookmarkResponse

router = APIRouter()


@router.post("/collections/{collection_id}/bookmarks", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    collection_id: int,
    data: BookmarkCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Verify collection exists
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Collection with id {collection_id} not found")

    bookmark = Bookmark(**data.model_dump(), collection_id=collection_id)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


@router.get("/collections/{collection_id}/bookmarks", response_model=list[BookmarkResponse])
async def list_bookmarks_by_collection(
    collection_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    # Verify collection exists
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Collection with id {collection_id} not found")

    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.collection_id == collection_id)
        .offset(skip)
        .limit(limit)
        .order_by(Bookmark.created_at.desc())
    )
    return result.scalars().all()


@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail=f"Bookmark with id {bookmark_id} not found")
    return bookmark


@router.patch("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail=f"Bookmark with id {bookmark_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bookmark, field, value)

    await db.commit()
    await db.refresh(bookmark)
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail=f"Bookmark with id {bookmark_id} not found")

    await db.delete(bookmark)
    await db.commit()
    return None
