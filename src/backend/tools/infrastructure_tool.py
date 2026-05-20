"""
Infrastructure Tool — OpenStreetMap Overpass API wrapper.

Fetches nearby critical infrastructure (hospitals, fire stations, police)
within a given radius using OpenStreetMap's public Overpass API.
"""

import json
import logging
from datetime import datetime, timezone

import httpx

from tools.interface import register_tool

logger = logging.getLogger(__name__)


def get_nearby_infrastructure(latitude: float, longitude: float, radius_meters: float = 5000.0) -> str:
    """
    Find nearby critical infrastructure (hospitals, police stations, fire stations) using OSM Overpass API.
    Completely free and open public API.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius_meters: Radius in meters (default 5000m)

    Returns:
        JSON string containing critical resources found with name, type, distance, and coordinates.
    """
    try:
        url = "https://overpass-api.de/api/interpreter"
        
        # Build Overpass QL query
        query = f"""
        [out:json][timeout:15];
        (
          node["amenity"="hospital"](around:{radius_meters},{latitude},{longitude});
          node["amenity"="police"](around:{radius_meters},{latitude},{longitude});
          node["amenity"="fire_station"](around:{radius_meters},{latitude},{longitude});
        );
        out body;
        """

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, data={"data": query})
            response.raise_for_status()
            data = response.json()

        elements = data.get("elements", [])
        results = []
        for elem in elements:
            tags = elem.get("tags", {})
            results.append({
                "id": elem.get("id"),
                "name": tags.get("name", tags.get("amenity", "Unnamed facility").replace("_", " ").title()),
                "type": tags.get("amenity"),
                "lat": elem.get("lat"),
                "lng": elem.get("lon"),
                "operator": tags.get("operator", "N/A"),
                "emergency": tags.get("emergency", "N/A")
            })

        return json.dumps({
            "source": "osm_overpass_api",
            "center": {"lat": latitude, "lng": longitude},
            "radius_meters": radius_meters,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_facilities": len(results),
            "facilities": results[:15]  # Limit to top 15 results
        }, indent=2)

    except Exception as e:
        logger.warning(f"OSM Overpass API failed: {e}. Using mock infrastructure fallback.")
        return _get_mock_infrastructure(latitude, longitude, radius_meters)


def _get_mock_infrastructure(latitude: float, longitude: float, radius_meters: float) -> str:
    """Fallback mock infrastructure resources matching Islamabad sectors."""
    mock = [
        {
            "id": "mock_inf_1",
            "name": "Pakistan Institute of Medical Sciences (PIMS)",
            "type": "hospital",
            "lat": 33.7126,
            "lng": 73.0485,
            "operator": "Government",
            "emergency": "yes"
        },
        {
            "id": "mock_inf_2",
            "name": "Shifa International Hospital",
            "type": "hospital",
            "lat": 33.6897,
            "lng": 73.0645,
            "operator": "Private",
            "emergency": "yes"
        },
        {
            "id": "mock_inf_3",
            "name": "G-10 Police Station",
            "type": "police",
            "lat": 33.7042,
            "lng": 73.0085,
            "operator": "ICT Police",
            "emergency": "yes"
        }
    ]
    return json.dumps({
        "source": "mock_fallback",
        "center": {"lat": latitude, "lng": longitude},
        "radius_meters": radius_meters,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_facilities": len(mock),
        "facilities": mock,
        "note": "Mock data — OSM Overpass API offline"
    }, indent=2)


register_tool("get_nearby_infrastructure", get_nearby_infrastructure)
