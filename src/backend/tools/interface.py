"""
CIRO Tool Interface & Routing System

Routes data requests to appropriate crisis data modules.
Modeled after SlashAgents' dataflows/interface.py pattern.

Each tool module (weather_tool, gdelt_tool, etc.) registers its functions here.
The agent_tools.py @tool wrappers call route_to_implementation() to dispatch.
"""

import logging
from typing import Callable, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TOOL CATEGORIES & ORGANIZATION
# ============================================================================

TOOLS_CATEGORIES = {
    "weather": {
        "description": "Weather forecasts, rainfall, temperature, wind",
        "tools": [
            "get_weather_data",
            "get_air_quality",
        ]
    },
    "social_signals": {
        "description": "Crisis news, social media signals, disaster reports",
        "tools": [
            "get_crisis_news",
            "search_crisis_news",
            "get_reliefweb_reports",
        ]
    },
    "traffic": {
        "description": "Real-time traffic flow, congestion, incidents",
        "tools": [
            "get_traffic_flow",
            "get_traffic_incidents",
        ]
    },
    "seismic": {
        "description": "Earthquake and seismic event data",
        "tools": [
            "get_earthquake_data",
        ]
    },
    "infrastructure": {
        "description": "Nearby hospitals, schools, shelters from OpenStreetMap",
        "tools": [
            "get_nearby_infrastructure",
        ]
    },
    "mock": {
        "description": "Pre-scripted demo scenario data for reliable demos",
        "tools": [
            "get_demo_scenario_data",
            "get_mock_signals",
        ]
    },
}


# ============================================================================
# METHOD REGISTRY (populated by tool modules on import)
# ============================================================================

METHOD_IMPLEMENTATIONS: Dict[str, Callable] = {}


def register_tool(name: str, func: Callable) -> None:
    """Register a tool implementation. Called by each tool module."""
    METHOD_IMPLEMENTATIONS[name] = func
    logger.debug(f"Registered tool: {name}")


# ============================================================================
# ROUTING FUNCTION (Public API)
# ============================================================================

def route_to_implementation(method: str, *args, **kwargs) -> Any:
    """
    Route method call to appropriate implementation.

    This is the main entry point for all data requests from @tool wrappers.
    Handles error handling and logging.

    Args:
        method: Tool method name (must be registered)
        *args: Positional arguments for the method
        **kwargs: Keyword arguments for the method

    Returns:
        Result from the method implementation (always a string for LangChain)

    Raises:
        ValueError: If method not supported
    """
    logger.info(f"Routing request for method: {method}")

    if method not in METHOD_IMPLEMENTATIONS:
        available = list(METHOD_IMPLEMENTATIONS.keys())
        raise ValueError(
            f"Method '{method}' not supported. "
            f"Available methods: {available}"
        )

    implementation = METHOD_IMPLEMENTATIONS[method]

    try:
        result = implementation(*args, **kwargs)
        logger.info(f"Successfully executed {method}")
        return result
    except Exception as e:
        logger.error(f"Error executing {method}: {e}")
        return f"ERROR: {method} failed — {str(e)}"


# ============================================================================
# TOOL DISCOVERY & METADATA
# ============================================================================

def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category.")


def list_available_tools() -> Dict[str, list]:
    """Get all available tools organized by category."""
    return {
        category: info["tools"]
        for category, info in TOOLS_CATEGORIES.items()
    }


def get_tool_info(method: str) -> Dict[str, Any]:
    """Get detailed information about a specific tool."""
    if method not in METHOD_IMPLEMENTATIONS:
        raise ValueError(f"Method '{method}' not found")

    category = get_category_for_method(method)
    implementation = METHOD_IMPLEMENTATIONS[method]

    return {
        "method": method,
        "category": category,
        "description": TOOLS_CATEGORIES[category]["description"],
        "implementation": implementation.__name__,
        "docstring": implementation.__doc__,
    }


def print_tools_summary():
    """Print a formatted summary of all available tools."""
    print("\n" + "=" * 70)
    print("AMAAN CIRO — AVAILABLE DATA TOOLS")
    print("=" * 70 + "\n")

    for category, info in TOOLS_CATEGORIES.items():
        registered = [t for t in info['tools'] if t in METHOD_IMPLEMENTATIONS]
        missing = [t for t in info['tools'] if t not in METHOD_IMPLEMENTATIONS]
        print(f"\n  {category.upper()}")
        print(f"    {info['description']}")
        for tool in registered:
            print(f"      [OK] {tool}")
        for tool in missing:
            print(f"      [  ] {tool} (not registered)")

    print("\n" + "=" * 70 + "\n")

