import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.signal_ingestion import SignalIngestionAgent
from src.backend.agents.crisis_classification import CrisisClassificationAgent
from src.backend.agents.severity_prediction import SeverityPredictionAgent
from src.backend.models.schemas import SignalIngestionInput, CrisisClassificationInput, SeverityPredictionInput

@pytest.mark.asyncio
async def test_phase2_integration():
    """
    Integration test chaining the 3 core agents of Phase 2.
    """
    # 1. Ingestion
    ingestion_agent = SignalIngestionAgent()
    ingestion_input = SignalIngestionInput(
        location={"lat": 33.7047, "lng": 73.0079, "city": "Islamabad", "address": "G-10"},
        radius_km=10.0,
        time_window_hours=2
    )
    # Force fallback by mocking httpx error or relying on timeout. We will just let it run.
    ingest_out = await ingestion_agent.run(ingestion_input)
    assert len(ingest_out.signals) > 0
    
    # 2. Classification
    classification_agent = CrisisClassificationAgent()
    # Mock gemini for stability in tests
    classification_agent.call_gemini = lambda prompt, fallback: ({
        "crisis_type": "urban_flood",
        "sub_type": "flash_flood",
        "confidence_score": 0.85,
        "contradictions_detected": False,
        "contradiction_detail": None,
        "dominant_signal_ids": [s.signal_id for s in ingest_out.signals],
        "dismissed_signal_ids": [],
        "dismissal_reasons": [],
        "reasoning": "Mocked for integration test"
    }, False)
    
    class_input = CrisisClassificationInput(
        signals=ingest_out.signals,
        location=ingestion_input.location,
        historical_context={"flood_vulnerability": 0.85, "low_income_flag": False}
    )
    class_out = await classification_agent.run(class_input)
    
    # 3. Severity
    severity_agent = SeverityPredictionAgent()
    sev_input = SeverityPredictionInput(
        crisis=class_out.primary_crisis,
        weather_data={"rainfall_mm": 82.0, "rainfall_intensity_mm_per_hr": 27.33},
        vulnerability_data={
            "flood_vulnerability": 0.85,
            "drainage_capacity_mm_per_hr": 12,
            "population_density_per_sqkm": 8500,
            "low_income_flag": False
        },
        historical_events=[]
    )
    sev_out = await severity_agent.run(sev_input)
    
    assert sev_out.severity_label in ["Minor", "Moderate", "Severe", "Critical", "Catastrophic"]
    
    # Traces from all 3 agents should exist
    assert "trace" in ingest_out.model_dump()
    assert "trace" in class_out.model_dump()
    assert "trace" in sev_out.model_dump()
    
    print("Phase 2 Integration Test Complete! Antigravity traces generated.")
