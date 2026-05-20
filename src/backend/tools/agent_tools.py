"""
CIRO Agent Tools — LangChain @tool decorated wrappers.
Mirrors SlashAgents' agents/utils/agent_tools.py pattern.

Each @tool routes through tools/interface.py for centralized error handling.
These tools can be bound to LangChain agents via llm.bind_tools().
"""

from langchain_core.tools import tool
from typing import Annotated
from tools.interface import route_to_implementation

# Import tool modules to trigger registration
import tools.weather_tool     # noqa: F401
import tools.gdelt_tool       # noqa: F401
import tools.traffic_tool     # noqa: F401
import tools.mock_tool        # noqa: F401
import tools.seismic_tool     # noqa: F401
import tools.infrastructure_tool # noqa: F401


# ============================================================================
# WEATHER TOOLS
# ============================================================================

@tool
def get_weather_forecast(
    latitude: Annotated[float, "Latitude coordinate"],
    longitude: Annotated[float, "Longitude coordinate"],
) -> str:
    """Get weather forecast including rainfall, temperature, and wind for given coordinates."""
    return route_to_implementation("get_weather_data", latitude, longitude)


@tool
def get_air_quality_index(
    latitude: Annotated[float, "Latitude coordinate"],
    longitude: Annotated[float, "Longitude coordinate"],
) -> str:
    """Get Air Quality Index (AQI) for given coordinates."""
    return route_to_implementation("get_air_quality", latitude, longitude)


# ============================================================================
# NEWS & SOCIAL SIGNAL TOOLS
# ============================================================================

@tool
def get_crisis_news_feed(
    location: Annotated[str, "City or region name (e.g., 'islamabad')"],
    keywords: Annotated[str, "Search keywords (e.g., 'flood disaster')"] = "flood disaster emergency",
) -> str:
    """Get real-time crisis news from GDELT for a location in Pakistan."""
    return route_to_implementation("get_crisis_news", location, keywords)


@tool
def search_news(
    query: Annotated[str, "Free text search query"],
) -> str:
    """Search crisis-related news by keyword."""
    return route_to_implementation("search_crisis_news", query)


# ============================================================================
# TRAFFIC TOOLS
# ============================================================================

@tool
def get_traffic_status(
    latitude: Annotated[float, "Latitude coordinate"],
    longitude: Annotated[float, "Longitude coordinate"],
) -> str:
    """Get real-time traffic flow and congestion level for given coordinates."""
    return route_to_implementation("get_traffic_flow", latitude, longitude)


@tool
def get_road_incidents(
    latitude: Annotated[float, "Latitude coordinate"],
    longitude: Annotated[float, "Longitude coordinate"],
) -> str:
    """Get traffic incidents and road closures near given coordinates."""
    return route_to_implementation("get_traffic_incidents", latitude, longitude)


# ============================================================================
# MOCK / DEMO TOOLS
# ============================================================================

@tool
def load_demo_scenario(
    scenario: Annotated[str, "Scenario name: 'scenario_a', 'scenario_b', or 'scenario_c'"] = "scenario_a",
) -> str:
    """Load pre-scripted demo scenario data for reliable demonstrations."""
    return route_to_implementation("get_demo_scenario_data", scenario)


@tool
def generate_mock_signals(
    location: Annotated[str, "Sector name (e.g., 'G-10')"] = "G-10",
    crisis_type: Annotated[str, "Crisis type: 'flood' or 'heatwave'"] = "flood",
) -> str:
    """Generate mock crisis signals for demo purposes."""
    return route_to_implementation("get_mock_signals", location, crisis_type)


# ============================================================================
# SEISMIC & INFRASTRUCTURE TOOLS
# ============================================================================

@tool
def get_recent_earthquakes(
    min_magnitude: Annotated[float, "Minimum magnitude threshold"] = 4.0,
    days_back: Annotated[int, "Number of days back to look"] = 7,
) -> str:
    """Fetch recent seismic events and earthquake notifications near Pakistan."""
    return route_to_implementation("get_earthquake_data", min_magnitude, days_back)


@tool
def get_nearby_critical_infrastructure(
    latitude: Annotated[float, "Latitude coordinate"],
    longitude: Annotated[float, "Longitude coordinate"],
    radius_meters: Annotated[float, "Search radius in meters"] = 5000.0,
) -> str:
    """Find nearby critical facilities (hospitals, police stations, fire stations) using OpenStreetMap."""
    return route_to_implementation("get_nearby_infrastructure", latitude, longitude, radius_meters)


@tool
def get_reliefweb_disaster_reports(
    query: Annotated[str, "Search query (e.g. 'flood', 'earthquake')"] = "Pakistan",
    limit: Annotated[int, "Max number of reports to return"] = 5,
) -> str:
    """Fetch recent situation reports and disaster updates from official ReliefWeb API."""
    return route_to_implementation("get_reliefweb_reports", query, limit)


# ============================================================================
# TOOL COLLECTIONS (for binding to specific agent nodes)
# ============================================================================

SIGNAL_INGESTION_TOOLS = [
    get_weather_forecast,
    get_crisis_news_feed,
    get_traffic_status,
    get_road_incidents,
    generate_mock_signals,
    get_recent_earthquakes,
    get_nearby_critical_infrastructure,
    get_reliefweb_disaster_reports,
]

CLASSIFICATION_TOOLS = [
    search_news,
    get_weather_forecast,
]

ALL_TOOLS = SIGNAL_INGESTION_TOOLS + [
    get_air_quality_index,
    load_demo_scenario,
    search_news,
]

