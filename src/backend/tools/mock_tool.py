"""
Mock Tool — Pre-scripted demo scenario data.
Loads from data/demo_scenarios.json for guaranteed demo reliability.
Used as fallback when all live APIs fail.
"""

import os
import json
import logging
from datetime import datetime, timezone
from tools.interface import register_tool

logger = logging.getLogger(__name__)

# Find data directory
_DATA_DIR = None
for candidate in [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"),
    os.path.join("/app", "data"),
]:
    if os.path.isdir(os.path.abspath(candidate)):
        _DATA_DIR = os.path.abspath(candidate)
        break


def get_demo_scenario_data(scenario: str = "scenario_a") -> str:
    """Load pre-scripted demo scenario data. Always succeeds."""
    try:
        if _DATA_DIR:
            path = os.path.join(_DATA_DIR, "demo_scenarios.json")
            with open(path, 'r') as f:
                data = json.load(f)
            if scenario in data:
                return json.dumps({"source": "demo_scenario", "scenario": scenario, "data": data[scenario]}, indent=2)
            return json.dumps({"source": "demo_scenario", "scenario": scenario, "data": data}, indent=2)
    except Exception as e:
        logger.warning(f"Failed to load demo scenario: {e}")
    return json.dumps({"source": "demo_scenario", "scenario": scenario, "data": {}, "error": "File not found"})


def get_mock_signals(location: str = "G-10", crisis_type: str = "flood") -> str:
    """Generate mock crisis signals for demo. Always succeeds."""
    now = datetime.now(timezone.utc).isoformat()
    signals = [
        {"signal_id": "mock-sig-001", "source": "mock", "signal_type": "weather",
         "content": f"Heavy rainfall of 82mm in 3 hours detected at {location}, Islamabad",
         "location": {"lat": 33.7047, "lng": 73.0079, "address": f"{location}, Islamabad"},
         "timestamp": now, "credibility_score": 0.92, "staleness_flag": False,
         "raw_data": {"rainfall_3h_mm": 82, "temperature_c": 31, "precipitation_now_mm": 28}},
        {"signal_id": "mock-sig-002", "source": "mock", "signal_type": "traffic",
         "content": f"Severe congestion on Jinnah Avenue near {location} — multiple roads waterlogged",
         "location": {"lat": 33.7050, "lng": 73.0090, "address": f"Jinnah Avenue, {location}"},
         "timestamp": now, "credibility_score": 0.87, "staleness_flag": False,
         "raw_data": {"congestion_level": "severe", "speed_kmh": 8}},
        {"signal_id": "mock-sig-003", "source": "mock", "signal_type": "social",
         "content": f"Multiple reports of flooding in {location} Markaz area — water entering basements",
         "location": {"lat": 33.7040, "lng": 73.0075, "address": f"{location} Markaz"},
         "timestamp": now, "credibility_score": 0.58, "staleness_flag": False,
         "raw_data": {"source": "gdelt_mock", "articles": 3}},
    ]
    if crisis_type == "flood":
        signals.append({
            "signal_id": "mock-sig-004", "source": "mock", "signal_type": "field_report",
            "content": f"Citizen report: water main burst at {location}/2, not flood-related",
            "location": {"lat": 33.7045, "lng": 73.0080, "address": f"{location}/2"},
            "timestamp": now, "credibility_score": 0.40, "staleness_flag": True,
            "raw_data": {"reporter": "anonymous", "verified": False}})
    return json.dumps({"source": "mock_signals", "total": len(signals), "signals": signals}, indent=2)


register_tool("get_demo_scenario_data", get_demo_scenario_data)
register_tool("get_mock_signals", get_mock_signals)
