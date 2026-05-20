import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.stakeholder_comms import StakeholderCommsAgent
from src.backend.models.schemas import (
    StakeholderCommsInput, CrisisObject, SeverityPrediction, 
    AllocationPlan, SimulationResult, StakeholderCommsOutput
)

@pytest.mark.asyncio
async def test_stakeholder_comms_agent():
    agent = StakeholderCommsAgent()
    
    # Mock dependencies (we can just use empty/dummy objects since we mock gemini)
    input_data = StakeholderCommsInput(
        crisis=CrisisObject(
            crisis_id="1", crisis_type="urban_flood", sub_type="flash",
            location={"lat": 33.7, "lng": 73.0, "sector": "G-10"},
            confidence_score=0.9, contradictions_detected=False, contradiction_detail=None,
            dominant_signals=[], dismissed_signals=[], status="active", trace={}
        ),
        severity=SeverityPrediction(
            severity_level=4, severity_label="Critical", affected_radius_km=2.0,
            affected_population=50000, estimated_duration_hours=10.0,
            peak_impact_time="2026", spread_risk=0.8, cascading_risks=[], uncertainty_range="", trace={}
        ),
        allocation=AllocationPlan(
            plan_id="p-1", crisis_allocations=[], unmet_needs=[], trade_off_explanation="",
            total_resources_deployed=10, estimated_cost_pkr=1000.0, fairness_check="", trace={}
        ),
        simulation=SimulationResult(
            simulation_id="s-1", before_state={"population_at_risk": 50000, "roads_blocked": [], "hospital_capacity_used_pct": 10.0, "estimated_casualties_if_unaddressed": 50, "response_coverage_pct": 0.0},
            response_actions=[], after_state={"population_at_risk": 5000, "roads_blocked": [], "hospital_capacity_used_pct": 10.0, "estimated_casualties_if_unaddressed": 5, "response_coverage_pct": 90.0},
            metrics={"response_time_improvement_pct": 40.0, "population_protected": 45000, "roads_rerouted": 1, "estimated_cost_pkr": 1000.0, "estimated_lives_protected": 45},
            baseline_comparison={"baseline_response_time_minutes": 45.0, "amaan_response_time_minutes": 15.0, "baseline_false_positive_rate": 0.0, "amaan_false_positive_rate": 0.0, "baseline_resource_utilization_pct": 50.0, "amaan_resource_utilization_pct": 90.0, "improvement_summary": ""},
            trace={}
        )
    )
    
    # Mock Gemini
    agent.call_gemini = lambda prompt, fallback: ({
        "messages": [
            {
                "audience": "Public", "channel": "SMS", "language": "Urdu/English",
                "subject": "Flood Warning / سیلاب کی وارننگ", "body": "Please evacuate. براہ کرم علاقہ خالی کریں۔",
                "urgency_level": "High", "sent_at": "2026-05-18T10:00:00Z"
            },
            {
                "audience": "Police", "channel": "Radio", "language": "English",
                "subject": "Deploy to G-10", "body": "Block access to G-10 markaz.",
                "urgency_level": "High", "sent_at": "2026-05-18T10:00:00Z"
            },
            {
                "audience": "Rescue 1122", "channel": "App", "language": "English",
                "subject": "Dispatch", "body": "4 boats dispatched.",
                "urgency_level": "Critical", "sent_at": "2026-05-18T10:00:00Z"
            },
            {
                "audience": "Hospitals", "channel": "Email", "language": "English",
                "subject": "Standby Alert", "body": "Prepare for influx.",
                "urgency_level": "High", "sent_at": "2026-05-18T10:00:00Z"
            },
            {
                "audience": "NDMA", "channel": "Dashboard", "language": "English",
                "subject": "SitRep", "body": "Flood contained.",
                "urgency_level": "Medium", "sent_at": "2026-05-18T10:00:00Z"
            }
        ]
    }, False)
    
    output = await agent.run(input_data)
    
    assert isinstance(output, StakeholderCommsOutput)
    assert len(output.messages) == 5
    audiences = [m.audience for m in output.messages]
    assert "Public" in audiences
    assert "NDMA" in audiences
    assert "trace" in output.model_dump()
