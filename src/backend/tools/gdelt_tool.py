"""
GDELT Tool — Crisis news and social signal fetcher.

Primary: GDELT Project v2 API (free, no key, unlimited)
Provides: Real-time crisis news articles, tone analysis, Pakistan coverage.

Falls back to mock news data if API is unavailable.
"""

import json
import logging
from datetime import datetime, timezone

import httpx

from tools.interface import register_tool

logger = logging.getLogger(__name__)


# ============================================================================
# GDELT NEWS SEARCH (Free, No Key)
# ============================================================================

def get_crisis_news(location: str, keywords: str = "flood disaster emergency") -> str:
    """
    Fetch crisis-related news from GDELT Project v2 API.
    Completely free, real-time, huge Pakistan coverage.

    Args:
        location: City or region name (e.g., "islamabad", "karachi")
        keywords: Space-separated search terms

    Returns JSON string with list of articles:
    - title, url, domain, language, seendate, tone
    """
    try:
        query = f"{keywords} {location} pakistan"
        query_encoded = query.replace(" ", "+")
        url = (
            f"https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={query_encoded}"
            f"&mode=artlist&maxrecords=15&format=json&timespan=24h"
        )

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        results = []
        for art in articles[:15]:
            results.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "domain": art.get("domain", ""),
                "language": art.get("language", ""),
                "seen_date": art.get("seendate", ""),
                "source_country": art.get("sourcecountry", ""),
                "tone": art.get("tone", 0),
            })

        return json.dumps({
            "source": "gdelt_v2",
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_articles": len(results),
            "articles": results,
        }, indent=2)

    except Exception as e:
        logger.warning(f"GDELT API failed: {e}. Using mock news data.")
        return _get_mock_news(location, keywords)


def search_crisis_news(query: str) -> str:
    """
    Free-text search on GDELT for crisis-related content.

    Args:
        query: Free text search query (e.g., "G-10 flooding Islamabad")

    Returns JSON string with matching articles.
    """
    try:
        query_encoded = query.replace(" ", "+")
        url = (
            f"https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={query_encoded}"
            f"&mode=artlist&maxrecords=10&format=json&timespan=48h"
        )

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        results = []
        for art in articles[:10]:
            results.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "domain": art.get("domain", ""),
                "tone": art.get("tone", 0),
                "seen_date": art.get("seendate", ""),
            })

        return json.dumps({
            "source": "gdelt_v2_search",
            "query": query,
            "total": len(results),
            "articles": results,
        }, indent=2)

    except Exception as e:
        logger.warning(f"GDELT search failed: {e}")
        return json.dumps({
            "source": "gdelt_v2_search",
            "query": query,
            "total": 0,
            "articles": [],
            "error": str(e),
        })


def _get_mock_news(location: str, keywords: str) -> str:
    """Fallback mock news data for demo reliability."""
    mock_articles = [
        {
            "title": f"Heavy rainfall causes flooding in {location} — residents urged to evacuate",
            "url": "https://example.com/mock-flood-1",
            "domain": "dawn.com",
            "language": "English",
            "seen_date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "source_country": "Pakistan",
            "tone": -3.5,
        },
        {
            "title": f"NDMA issues flood alert for multiple sectors in {location}",
            "url": "https://example.com/mock-flood-2",
            "domain": "geo.tv",
            "language": "English",
            "seen_date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "source_country": "Pakistan",
            "tone": -4.1,
        },
        {
            "title": f"Traffic disrupted on major roads in {location} due to waterlogging",
            "url": "https://example.com/mock-flood-3",
            "domain": "tribune.com.pk",
            "language": "English",
            "seen_date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "source_country": "Pakistan",
            "tone": -2.8,
        },
    ]

    return json.dumps({
        "source": "mock_fallback",
        "query": f"{keywords} {location} pakistan",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(mock_articles),
        "articles": mock_articles,
        "note": "Mock data — GDELT API unavailable"
    }, indent=2)


def get_reliefweb_reports(query: str = "Pakistan", limit: int = 5) -> str:
    """
    Fetch recent disaster reports and situation updates from the official ReliefWeb API.
    Completely free, open public API.

    Args:
        query: Search query (e.g., "flood Pakistan", "earthquake")
        limit: Max number of reports to return (default 5)

    Returns:
        JSON string containing matching ReliefWeb reports with title, URL, source, and summary.
    """
    try:
        url = "https://api.reliefweb.int/v1/reports"
        params = {
            "appname": "amaan-ciro",
            "query[value]": f"{query} Pakistan",
            "limit": limit,
            "sort[]": "date:desc",
            "profile": "list"
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        reports = data.get("data", [])
        results = []
        for report in reports:
            fields = report.get("fields", {})
            results.append({
                "title": fields.get("title", ""),
                "url": fields.get("url", ""),
                "date": fields.get("date", {}).get("created", ""),
                "primary_country": "Pakistan",
                "source": ", ".join([s.get("name", "") for s in fields.get("source", [])])
            })

        return json.dumps({
            "source": "reliefweb_api",
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_reports": len(results),
            "reports": results
        }, indent=2)

    except Exception as e:
        logger.warning(f"ReliefWeb API failed: {e}. Using mock reports fallback.")
        return _get_mock_reliefweb(query)


def _get_mock_reliefweb(query: str) -> str:
    """Fallback mock ReliefWeb data for robust error handling."""
    mock = [
        {
            "title": "Pakistan: Monsoon rains and flooding - Situation Report No. 3",
            "url": "https://reliefweb.int/report/pakistan/monsoon-rains-flooding-situation-report",
            "date": datetime.now(timezone.utc).isoformat(),
            "primary_country": "Pakistan",
            "source": "OCHA"
        },
        {
            "title": "Pakistan: Severe Weather and Floods DREF Application",
            "url": "https://reliefweb.int/report/pakistan/dref-application-floods",
            "date": datetime.now(timezone.utc).isoformat(),
            "primary_country": "Pakistan",
            "source": "IFRC"
        }
    ]
    return json.dumps({
        "source": "mock_fallback",
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_reports": len(mock),
        "reports": mock,
        "note": "Mock data — ReliefWeb API offline"
    }, indent=2)


# ============================================================================
# REGISTER TOOLS
# ============================================================================
register_tool("get_crisis_news", get_crisis_news)
register_tool("search_crisis_news", search_crisis_news)
register_tool("get_reliefweb_reports", get_reliefweb_reports)

