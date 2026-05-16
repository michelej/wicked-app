from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

from app.core.config import settings
from app.models.watch_item import WatchSearchResult


class TmdbService:
    def __init__(self):
        self.base_url = settings.TMDB_BASE_URL.rstrip("/")
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL.rstrip("/")
        self.api_key = settings.TMDB_API_KEY

    def ensure_api_key(self) -> None:
        if self.api_key:
            return

        raise ValueError("TMDB_API_KEY no está configurada en backend/.env")

    async def search(self, query: str, media_type: str = "multi", page: int = 1) -> list[WatchSearchResult]:
        self.ensure_api_key()

        allowed_media_types = {"multi", "movie", "tv"}
        selected_media_type = media_type if media_type in allowed_media_types else "multi"

        endpoint = "/search/multi" if selected_media_type == "multi" else f"/search/{selected_media_type}"
        response = self._fetch_json(endpoint, {
            "api_key": self.api_key,
            "query": query,
            "page": page,
            "language": "es-ES",
            "include_adult": "false",
        })

        results = []
        for item in response.get("results", []):
            normalized = self._normalize_item(item)
            if normalized:
                results.append(normalized)

        return results

    def _fetch_json(self, endpoint: str, params: dict) -> dict:
        request_params = {**params}
        headers = {
            "accept": "application/json",
            "user-agent": "wicked-app/1.0",
        }

        if self.api_key.startswith("eyJ"):
            headers["Authorization"] = f"Bearer {self.api_key}"
            request_params.pop("api_key", None)

        url = f"{self.base_url}{endpoint}?{urlencode(request_params)}"
        request = Request(url, headers=headers)

        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
                message = payload.get("status_message") or payload.get("message") or str(error)
            except Exception:
                message = str(error)

            raise ValueError(message) from error

    def _normalize_item(self, item: dict) -> Optional[WatchSearchResult]:
        media_type = item.get("media_type")
        if media_type not in {"movie", "tv"}:
            return None

        title = item.get("title") or item.get("name")
        if not title:
            return None

        original_title = item.get("original_title") or item.get("original_name")
        release_date = item.get("release_date") or item.get("first_air_date")
        poster_path = self._build_image_url(item.get("poster_path"))
        backdrop_path = self._build_image_url(item.get("backdrop_path"))

        return WatchSearchResult(
            tmdb_id=item["id"],
            media_type=media_type,
            title=title,
            original_title=original_title,
            overview=item.get("overview"),
            poster_path=poster_path,
            backdrop_path=backdrop_path,
            release_date=release_date,
            genre_ids=item.get("genre_ids", []),
            vote_average=item.get("vote_average"),
        )

    def _build_image_url(self, image_path: Optional[str]) -> Optional[str]:
        if not image_path:
            return None

        return f"{self.image_base_url}{image_path}"
