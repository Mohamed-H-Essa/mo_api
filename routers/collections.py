from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from database import get_db
from models import Collection
from schemas import CollectionCreate, CollectionUpdate, CollectionResponse

router = APIRouter()


@router.post("", response_model=CollectionResponse, status_code=201)
async def create_collection(
    data: CollectionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    collection = Collection(**data.model_dump())
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    result = await db.execute(
        select(Collection).offset(skip).limit(limit).order_by(Collection.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection with id {collection_id} not found")
    return collection


@router.patch("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection with id {collection_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)

    await db.commit()
    await db.refresh(collection)
    return collection


@router.delete("/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection with id {collection_id} not found")

    await db.delete(collection)
    await db.commit()
    return None
