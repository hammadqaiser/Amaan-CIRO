import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.signal_ingestion import SignalIngestionAgent
from src.backend.agents.crisis_classification import CrisisClassificationAgent
from src.backend.agents.resource_allocation import ResourceAllocationAgent
from src.backend.agents.verification import VerificationAgent
from src.backend.models.schemas import (
    SignalIngestionInput, CrisisClassificationInput, 
    ResourceAllocationInput, ResourceInventory, AllocationConstraints,
    VerificationInput, CrisisObject, RawSignal
)

@pytest.mark.asyncio
async def test_pmd_api_fallback():
    # PMD API returns 500 -> uses mock fallback
    os.environ["DEMO_MODE"] = "1" # Force fallback
    agent = SignalIngestionAgent()
    input_data = SignalIngestionInput(location={"lat": 33.7, "lng": 73.0, "sector": "G-10"})
    result = await agent.run(input_data)
    
    assert result.fallback_used is True
    assert len(result.signals) > 0
    assert result.trace["fallback_triggered"] is True

@pytest.mark.asyncio
async def test_gemini_api_timeout_fallback():
    # Gemini API timeout -> uses rule-based fallback
    agent = CrisisClassificationAgent()
    
    # Save original
    original_call = agent.call_gemini
    agent.call_gemini = lambda prompt, fallback: (fallback, True)
    
    try:
        input_data = CrisisClassificationInput(
            signals=[
                RawSignal(signal_id="1", source="mock", signal_type="weather", content="heavy rain", location={}, timestamp="2026-05-18T10:00:00Z", credibility_score=0.9, staleness_flag=False, raw_data={}),
                RawSignal(signal_id="2", source="mock", signal_type="social", content="flood", location={}, timestamp="2026-05-18T10:00:00Z", credibility_score=0.8, staleness_flag=False, raw_data={})
            ],
            location={},
            historical_context={}
        )
        result = await agent.run(input_data)
        
        assert result.primary_crisis.crisis_type == "urban_flood"
        assert result.classification_method == "rule_based_fallback"
        assert result.trace["fallback_triggered"] is True
    finally:
        agent.call_gemini = original_call

@pytest.mark.asyncio
async def test_two_crises_in_60s():
    # Two crises arrive -> Resource allocation handles both with trade-off
    agent = ResourceAllocationAgent()
    crisis1 = CrisisObject(crisis_id="1", crisis_type="urban_flood", sub_type="", location={"sector":"G-10"}, confidence_score=0.9, contradictions_detected=False, contradiction_detail=None, dominant_signals=[], dismissed_signals=[], status="active", trace={})
    crisis2 = CrisisObject(crisis_id="2", crisis_type="heatwave", sub_type="", location={"sector":"I-8"}, confidence_score=0.8, contradictions_detected=False, contradiction_detail=None, dominant_signals=[], dismissed_signals=[], status="active", trace={})
    
    # Needs Severity predictions too for both
    from src.backend.models.schemas import SeverityPrediction
    sev1 = SeverityPrediction(severity_level=4, severity_label="Critical", affected_radius_km=5, affected_population=10000, estimated_duration_hours=10, peak_impact_time="", spread_risk=0.8, cascading_risks=[], uncertainty_range="", trace={})
    sev2 = SeverityPrediction(severity_level=3, severity_label="Severe", affected_radius_km=3, affected_population=5000, estimated_duration_hours=24, peak_impact_time="", spread_risk=0.5, cascading_risks=[], uncertainty_range="", trace={})
    
    inv = ResourceInventory(ambulances={"total": 10, "available": 2, "locations": []}, rescue_boats={"total": 5, "available": 5, "locations": []}, rescue_teams={"total": 5, "available": 5, "locations": []}, police_traffic_units={"total": 5, "available": 5, "locations": []}, medical_outreach_teams={"total": 5, "available": 5, "locations": []}, water_tankers={"total": 5, "available": 5, "locations": []}, generators={"total": 5, "available": 5, "locations": []}, shelters=[])
    
    input_data = ResourceAllocationInput(
        crises=[crisis1, crisis2],
        severity_predictions=[sev1, sev2],
        resource_inventory=inv,
        constraints=AllocationConstraints()
    )
    result = await agent.run(input_data)
    
    assert len(result.crisis_allocations) == 2
    assert "trade-off" in result.trade_off_explanation.lower() or len(result.unmet_needs) > 0 or result.trace["fallback_triggered"]

@pytest.mark.asyncio
async def test_contradicting_field_report_retraction():
    # VerificationAgent receives contradicting field report -> retracts alert
    from datetime import datetime, timezone
    agent = VerificationAgent()
    crisis = CrisisObject(crisis_id="1", crisis_type="urban_flood", sub_type="", location={"sector":"G-10"}, confidence_score=0.5, contradictions_detected=False, contradiction_detail=None, dominant_signals=[], dismissed_signals=[], status="active", trace={})
    
    new_signal = RawSignal(
        signal_id="verify1",
        source="citizen_app",
        signal_type="field_report",
        content="False alarm! It is just a water main burst, no rain or flood.",
        location={},
        timestamp=datetime.now(timezone.utc).isoformat(),
        credibility_score=0.95,
        staleness_flag=False,
        raw_data={}
    )
    
    input_data = VerificationInput(
        crisis=crisis,
        new_signals=[new_signal],
        original_classification_trace={},
        trigger_mode="contradiction_detected"
    )
    result = await agent.run(input_data)
    
    assert result.verdict == "retracted"
    assert result.updated_crisis.status == "retracted"
    assert "water main" in (result.retraction_reason or "").lower() or result.trace["fallback_triggered"]
