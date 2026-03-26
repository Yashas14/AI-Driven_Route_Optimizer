# SmartRoute Pro — Geocoding via OpenStreetMap Nominatim
# Developed by Yashas D and M Shivani Kashyap | Team: TechTriad

import logging
from functools import lru_cache
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "SmartRoutePro/2.0"}


@lru_cache(maxsize=256)
def geocode(address: str) -> Optional[Tuple[float, float, str]]:
    """Convert an address to (lat, lon, display_name) using OpenStreetMap Nominatim.

    Returns None if the address cannot be geocoded.
    """
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            r = results[0]
            return float(r["lat"]), float(r["lon"]), r.get("display_name", address)
    except Exception as e:
        logger.warning(f"Geocoding failed for '{address}': {e}")
    return None
