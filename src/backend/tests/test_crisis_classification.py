import pytest
import os
import sys
import json
from datetime import datetime

# Add parent directory to path so src.backend... works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.crisis_classification import CrisisClassificationAgent
from src.backend.models.schemas import CrisisClassificationInput, RawSignal, CrisisClassificationOutput

@pytest.mark.asyncio
async def test_crisis_classification_contradiction_resolution():
    agent = CrisisClassificationAgent()
    
    # We will use the explicit scenario A contradiction logic
    signals = [
        RawSignal(
            signal_id="sig-001",
            source="open-meteo",
            signal_type="weather",
            content="82mm rainfall in past 3 hours",
            location={"lat": 33.7047, "lng": 73.0079},
            timestamp="2026-05-18T14:32:00Z",
            credibility_score=0.92,
            staleness_flag=False,
            raw_data={}
        ),
        RawSignal(
            signal_id="sig-002",
            source="google_traffic",
            signal_type="traffic",
            content="Severe congestion on Jinnah Ave",
            location={"lat": 33.7047, "lng": 73.0079},
            timestamp="2026-05-18T14:30:00Z",
            credibility_score=0.87,
            staleness_flag=False,
            raw_data={}
        ),
        RawSignal(
            signal_id="sig-003",
            source="gdelt",
            signal_type="social",
            content="Water entering basements in G-10 markaz, cars submerged",
            location={"lat": 33.7047, "lng": 73.0079},
            timestamp="2026-05-18T14:15:00Z",
            credibility_score=0.58,
            staleness_flag=False,
            raw_data={}
        ),
        RawSignal(
            signal_id="sig-004",
            source="citizen_app",
            signal_type="field_report",
            content="Water main burst, not a flood",
            location={"lat": 33.7047, "lng": 73.0079},
            timestamp="2026-05-18T10:00:00Z",
            credibility_score=0.40,  # Adjusted by SignalIngestion due to staleness
            staleness_flag=True,
            raw_data={}
        )
    ]
    
    input_data = CrisisClassificationInput(
        signals=signals,
        location={"lat": 33.7047, "lng": 73.0079},
        historical_context={"flood_vulnerability": 0.85, "low_income_flag": False}
    )
    
    # Mock call_gemini to simulate successful Gemini response
    agent.call_gemini = lambda prompt, fallback: ({
        "crisis_type": "urban_flood",
        "sub_type": "flash_flood",
        "confidence_score": 0.82,
        "contradictions_detected": True,
        "contradiction_detail": "Dismissed stale water main report in favor of recent meteorological data.",
        "dominant_signal_ids": ["sig-001", "sig-002"],
        "dismissed_signal_ids": ["sig-004"],
        "dismissal_reasons": ["Stale and low credibility"],
        "reasoning": "Classified as flood due to high-credibility weather data."
    }, False)
    
    output = await agent.run(input_data)
    
    assert isinstance(output, CrisisClassificationOutput)
    crisis = output.primary_crisis
    
    # Check that it resolved the contradiction in favor of the flood
    assert crisis.crisis_type == "urban_flood"
    
    # Signal 004 should be dismissed
    assert "sig-004" in crisis.dismissed_signals
    
    # Confidence should be penalized but remain > 0.50
    assert crisis.confidence_score > 0.50
    
    # Trace must be generated
    assert "trace" in output.model_dump()
    assert output.trace["agent"] == "CrisisClassificationAgent"
