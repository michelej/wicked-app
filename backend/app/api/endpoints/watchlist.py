from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.watch_item import WatchItem, WatchItemCreate, WatchItemUpdate, WatchSearchResult
from app.services.tmdb_service import TmdbService
from app.services.watchlist_service import WatchlistService


router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=List[WatchItem])
async def get_watchlist_items(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    media_type: Optional[str] = Query(default=None, alias="mediaType"),
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = WatchlistService(db)
    return await service.get_items(status=status_filter, media_type=media_type, search=search, skip=skip, limit=limit)


@router.post("", response_model=WatchItem, status_code=status.HTTP_201_CREATED)
async def create_watchlist_item(
    payload: WatchItemCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = WatchlistService(db)
    try:
        return await service.create_item(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{item_id}", response_model=WatchItem)
async def update_watchlist_item(
    item_id: str,
    payload: WatchItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = WatchlistService(db)
    item = await service.update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Watch item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = WatchlistService(db)
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watch item not found")


@router.get("/search/tmdb", response_model=List[WatchSearchResult])
async def search_tmdb_catalog(
    q: str = Query(..., min_length=2),
    media_type: str = Query(default="multi", alias="mediaType"),
    page: int = Query(default=1, ge=1, le=5),
):
    service = TmdbService()
    try:
        return await service.search(q, media_type=media_type, page=page)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar TMDb: {error}") from error
