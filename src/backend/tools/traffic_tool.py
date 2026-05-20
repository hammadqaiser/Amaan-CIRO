"""
Traffic Tool — TomTom Traffic Flow API wrapper.
Primary: TomTom (free tier, 2500/day, needs key)
Fallback: Mock traffic data for demo scenarios.
"""

import os
import json
import logging
from datetime import datetime, timezone
import httpx
from tools.interface import register_tool

logger = logging.getLogger(__name__)


def get_traffic_flow(latitude: float, longitude: float) -> str:
    """Fetch real-time traffic flow from TomTom. Falls back to mock data."""
    api_key = os.environ.get("TOMTOM_API_KEY")
    if not api_key:
        return _get_mock_traffic(latitude, longitude)
    try:
        url = (
            f"https://api.tomtom.com/traffic/services/4/flowSegmentData"
            f"/absolute/10/json?point={latitude},{longitude}&key={api_key}"
        )
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
        flow = data.get("flowSegmentData", {})
        current_speed = flow.get("currentSpeed", 0)
        free_flow = flow.get("freeFlowSpeed", 60)
        congestion = 1.0 - (current_speed / free_flow) if free_flow > 0 else 0
        return json.dumps({
            "source": "tomtom", "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_speed_kmh": current_speed, "free_flow_speed_kmh": free_flow,
            "congestion_ratio": round(congestion, 3),
            "congestion_level": "severe" if congestion > 0.8 else "heavy" if congestion > 0.6 else "moderate" if congestion > 0.4 else "light",
            "road_closure": flow.get("roadClosure", False),
        }, indent=2)
    except Exception as e:
        logger.warning(f"TomTom failed: {e}")
        return _get_mock_traffic(latitude, longitude)


def get_traffic_incidents(latitude: float, longitude: float) -> str:
    """Fetch traffic incidents near location. Falls back to mock."""
    api_key = os.environ.get("TOMTOM_API_KEY")
    if not api_key:
        return _get_mock_incidents()
    try:
        delta = 5.0 / 111.0
        bbox = f"{longitude-delta},{latitude-delta},{longitude+delta},{latitude+delta}"
        url = f"https://api.tomtom.com/traffic/services/5/incidentDetails?bbox={bbox}&key={api_key}&language=en-US"
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
        incidents = [{"id": inc.get("properties",{}).get("id",""), "description": inc.get("properties",{}).get("description","")} for inc in data.get("incidents",[])[:10]]
        return json.dumps({"source": "tomtom_incidents", "total": len(incidents), "incidents": incidents}, indent=2)
    except Exception as e:
        logger.warning(f"TomTom incidents failed: {e}")
        return _get_mock_incidents()


def _get_mock_traffic(lat: float, lng: float) -> str:
    return json.dumps({
        "source": "mock_fallback", "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_speed_kmh": 12, "free_flow_speed_kmh": 50, "congestion_ratio": 0.76,
        "congestion_level": "heavy", "road_closure": False,
        "note": "Mock data — TomTom unavailable"
    }, indent=2)


def _get_mock_incidents() -> str:
    return json.dumps({
        "source": "mock_fallback", "total": 2,
        "incidents": [
            {"id": "INC-MOCK-001", "description": "Road flooded — Jinnah Ave near G-10 Markaz", "road_closed": True},
            {"id": "INC-MOCK-002", "description": "Heavy congestion on 7th Avenue", "road_closed": False},
        ]
    }, indent=2)


register_tool("get_traffic_flow", get_traffic_flow)
register_tool("get_traffic_incidents", get_traffic_incidents)
