"""HTTP client for official Argentine public data APIs."""

from __future__ import annotations

from io import StringIO
from typing import Any

import httpx
import pandas as pd

SERIES_API_URL = "https://apis.datos.gob.ar/series/api"
GEOREF_API_URL = "https://apis.datos.gob.ar/georef/api"


class ArgentinaDataClient:
    """Small synchronous client for the Series and Georef APIs."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> ArgentinaDataClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def search_series(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        """Search statistical series and return the API's result document."""
        if not query.strip():
            raise ValueError("Search query cannot be empty.")
        if limit < 1:
            raise ValueError("Limit must be greater than zero.")

        response = self._client.get(
            f"{SERIES_API_URL}/search",
            params={"query": query, "limit": limit, "pretty": "true"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ValueError("The Series API returned an unexpected search response.")
        return payload

    def fetch_series(
        self,
        ids: list[str],
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 5000,
    ) -> pd.DataFrame:
        """Download observations for one or more Series API field IDs."""
        clean_ids = [series_id.strip() for series_id in ids if series_id.strip()]
        if not clean_ids:
            raise ValueError("At least one series ID is required.")
        if limit < 1:
            raise ValueError("Limit must be greater than zero.")

        params: dict[str, str | int] = {
            "ids": ",".join(clean_ids),
            "limit": limit,
            "format": "csv",
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = self._client.get(f"{SERIES_API_URL}/series", params=params)
        response.raise_for_status()
        frame = pd.read_csv(StringIO(response.text))
        if frame.empty or len(frame.columns) < 2:
            raise ValueError("The Series API returned no observations.")
        return frame

    def list_provinces(self) -> list[dict[str, str]]:
        """Return the Argentine provinces listed by the Georef API."""
        response = self._client.get(
            f"{GEOREF_API_URL}/provincias",
            params={"campos": "id,nombre", "max": 100},
        )
        response.raise_for_status()
        payload = response.json()
        provinces = payload.get("provincias") if isinstance(payload, dict) else None
        if not isinstance(provinces, list):
            raise ValueError("The Georef API returned an unexpected provinces response.")
        return provinces
