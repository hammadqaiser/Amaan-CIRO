"""
Seismic Tool — USGS Earthquake API wrapper.

Provides real-time seismic event notifications and details near Pakistan.
"""

import json
import logging
from datetime import datetime, timedelta, timezone

import httpx

from tools.interface import register_tool

logger = logging.getLogger(__name__)


def get_earthquake_data(min_magnitude: float = 4.0, days_back: int = 7) -> str:
    """
    Fetch recent seismic events near Pakistan using USGS Earthquake API.
    Completely free, open public API.

    Args:
        min_magnitude: Minimum magnitude threshold (default 4.0)
        days_back: Number of days back to look (default 7)

    Returns:
        JSON string containing list of earthquakes with magnitude, place, time, and coordinates.
    """
    try:
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days_back)

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": start_time.isoformat(),
            "endtime": end_time.isoformat(),
            "minmagnitude": min_magnitude,
            # Focus on Pakistan region coordinates box: Lat 23 to 38, Lng 60 to 78
            "minlatitude": 23.0,
            "maxlatitude": 38.0,
            "minlongitude": 60.0,
            "maxlongitude": 78.0
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        features = data.get("features", [])
        results = []
        for feature in features:
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [0, 0, 0])
            
            # Extract timestamp
            time_ms = props.get("time", 0)
            time_iso = datetime.fromtimestamp(time_ms / 1000.0, tz=timezone.utc).isoformat()

            results.append({
                "id": feature.get("id"),
                "magnitude": props.get("mag"),
                "place": props.get("place"),
                "time": time_iso,
                "lat": coords[1],
                "lng": coords[0],
                "depth_km": coords[2],
                "url": props.get("url")
            })

        return json.dumps({
            "source": "usgs_seismic_api",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events": len(results),
            "events": results
        }, indent=2)

    except Exception as e:
        logger.warning(f"USGS Earthquake API failed: {e}. Using mock earthquake data.")
        return _get_mock_earthquake_data()


def _get_mock_earthquake_data() -> str:
    """Fallback mock earthquake data near Pakistan."""
    mock = [
        {
            "id": "mock_quake_1",
            "magnitude": 4.8,
            "place": "68 km NNE of Khuzdar, Pakistan",
            "time": datetime.now(timezone.utc).isoformat(),
            "lat": 28.38,
            "lng": 66.82,
            "depth_km": 10.0,
            "url": "https://earthquake.usgs.gov"
        }
    ]
    return json.dumps({
        "source": "mock_fallback",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_events": len(mock),
        "events": mock,
        "note": "Mock data — USGS API offline"
    }, indent=2)


register_tool("get_earthquake_data", get_earthquake_data)
