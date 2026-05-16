from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


WatchStatus = Literal["to_watch", "watching", "watched"]
MediaType = Literal["movie", "tv"]


class WatchSeasonProgress(BaseModel):
    watched_seasons: Optional[int] = Field(default=None, ge=0)
    watched_episodes: Optional[int] = Field(default=None, ge=0)
    total_seasons: Optional[int] = Field(default=None, ge=0)
    total_episodes: Optional[int] = Field(default=None, ge=0)


class WatchItemBase(BaseModel):
    tmdb_id: int = Field(..., ge=1)
    media_type: MediaType
    title: str = Field(..., min_length=1, max_length=240)
    original_title: Optional[str] = Field(default=None, max_length=240)
    overview: Optional[str] = Field(default=None, max_length=4000)
    poster_path: Optional[str] = Field(default=None, max_length=500)
    backdrop_path: Optional[str] = Field(default=None, max_length=500)
    release_date: Optional[str] = Field(default=None, max_length=32)
    genres: List[str] = Field(default_factory=list)
    status: WatchStatus = "to_watch"
    personal_rating: Optional[float] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = Field(default=None, max_length=2000)
    tags: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    watched_at: Optional[datetime] = None
    season_progress: Optional[WatchSeasonProgress] = None


class WatchItemCreate(WatchItemBase):
    pass


class WatchItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=240)
    original_title: Optional[str] = Field(default=None, max_length=240)
    overview: Optional[str] = Field(default=None, max_length=4000)
    poster_path: Optional[str] = Field(default=None, max_length=500)
    backdrop_path: Optional[str] = Field(default=None, max_length=500)
    release_date: Optional[str] = Field(default=None, max_length=32)
    genres: Optional[List[str]] = None
    status: Optional[WatchStatus] = None
    personal_rating: Optional[float] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = Field(default=None, max_length=2000)
    tags: Optional[List[str]] = None
    started_at: Optional[datetime] = None
    watched_at: Optional[datetime] = None
    season_progress: Optional[WatchSeasonProgress] = None


class WatchItem(WatchItemBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class WatchSearchResult(BaseModel):
    tmdb_id: int
    media_type: MediaType
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    genre_ids: List[int] = Field(default_factory=list)
    vote_average: Optional[float] = None
    total_seasons: Optional[int] = Field(default=None, ge=0)
    total_episodes: Optional[int] = Field(default=None, ge=0)
