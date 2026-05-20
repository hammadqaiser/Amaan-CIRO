"""
Weather Tool — Open-Meteo + OpenWeatherMap API wrappers.

Primary: Open-Meteo (free, no key, 10,000 calls/day)
Backup:  OpenWeatherMap (free tier, 1000 calls/day, needs key)
Fallback: Mock weather data from demo_scenarios.json

Provides: rainfall_mm, temperature, wind speed, precipitation intensity.
"""

import os
import json
import logging
from datetime import datetime, timezone

import httpx

from tools.interface import register_tool

logger = logging.getLogger(__name__)

# Data directory for mock fallbacks
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "..", "data")
if not os.path.isdir(_DATA_DIR):
    _DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ============================================================================
# OPEN-METEO (Primary — Free, No Key)
# ============================================================================

def get_weather_data(latitude: float, longitude: float) -> str:
    """
    Fetch current weather + hourly forecast from Open-Meteo.
    Free, no API key required, 10,000 calls/day limit.

    Returns JSON string with:
    - current_weather: temperature, windspeed, weathercode
    - hourly: precipitation, temperature_2m, windspeed_10m (next 24h)
    - rainfall_3h_mm: sum of precipitation in last 3 hours
    - precipitation_now_mm: current hour precipitation

    On failure: returns mock weather data.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            f"&hourly=precipitation,temperature_2m,windspeed_10m"
            f"&current_weather=true"
            f"&timezone=Asia/Karachi"
            f"&forecast_days=1"
        )

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        # Extract key metrics
        current = data.get("current_weather", {})
        hourly = data.get("hourly", {})
        precip = hourly.get("precipitation", [])

        # Calculate 3-hour rainfall sum (last 3 entries)
        now_hour = datetime.now(timezone.utc).hour
        recent_precip = precip[max(0, now_hour - 3):now_hour + 1] if precip else []
        rainfall_3h = sum(recent_precip) if recent_precip else 0.0

        result = {
            "source": "open_meteo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": current.get("temperature", 30),
            "windspeed_kmh": current.get("windspeed", 10),
            "weathercode": current.get("weathercode", 0),
            "rainfall_3h_mm": round(rainfall_3h, 1),
            "precipitation_now_mm": precip[now_hour] if now_hour < len(precip) else 0.0,
            "hourly_precipitation": precip[:24] if precip else [],
            "hourly_temperature": hourly.get("temperature_2m", [])[:24],
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.warning(f"Open-Meteo failed: {e}. Using mock weather data.")
        return _get_mock_weather(latitude, longitude)


def _get_mock_weather(latitude: float, longitude: float) -> str:
    """Fallback mock weather data for demo reliability."""
    mock = {
        "source": "mock_fallback",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 34.2,
        "windspeed_kmh": 15.0,
        "weathercode": 65,  # Heavy rain
        "rainfall_3h_mm": 82.0,
        "precipitation_now_mm": 28.5,
        "hourly_precipitation": [12.0, 18.5, 23.0, 28.5, 15.0, 8.0],
        "hourly_temperature": [33.0, 32.5, 31.8, 31.0, 30.5, 30.0],
        "note": "Mock data — Open-Meteo API unavailable"
    }
    return json.dumps(mock, indent=2)


# ============================================================================
# OPENWEATHERMAP AQI (Bonus — requires free key)
# ============================================================================

def get_air_quality(latitude: float, longitude: float) -> str:
    """
    Fetch Air Quality Index from OpenWeatherMap.
    Requires OPENWEATHERMAP_API_KEY environment variable.
    Free tier: 1000 calls/day.

    Returns AQI (1-5 scale), CO, NO2, PM2.5, PM10.
    """
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return json.dumps({
            "source": "openweathermap_aqi",
            "error": "OPENWEATHERMAP_API_KEY not set",
            "aqi": 2,
            "note": "Default moderate AQI assumed"
        })

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={latitude}&lon={longitude}&appid={api_key}"
        )

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        aqi_data = data.get("list", [{}])[0]
        components = aqi_data.get("components", {})

        result = {
            "source": "openweathermap_aqi",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "aqi": aqi_data.get("main", {}).get("aqi", 2),
            "co": components.get("co", 0),
            "no2": components.get("no2", 0),
            "pm2_5": components.get("pm2_5", 0),
            "pm10": components.get("pm10", 0),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.warning(f"OpenWeatherMap AQI failed: {e}")
        return json.dumps({
            "source": "openweathermap_aqi",
            "error": str(e),
            "aqi": 2,
            "note": "Fallback moderate AQI"
        })


# ============================================================================
# REGISTER TOOLS
# ============================================================================
register_tool("get_weather_data", get_weather_data)
register_tool("get_air_quality", get_air_quality)
