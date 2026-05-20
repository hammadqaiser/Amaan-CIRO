import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.simulation import SimulationAgent
from src.backend.models.schemas import (
    SimulationInput, CrisisObject, SeverityPrediction, AllocationPlan, SimulationResult
)

@pytest.mark.asyncio
async def test_simulation_agent():
    agent = SimulationAgent()
    
    # Mock dependencies
    crisis = CrisisObject(
        crisis_id="c-1",
        crisis_type="urban_flood",
        sub_type="flash_flood",
        location={"lat": 33.70, "lng": 73.00, "sector": "G-10", "low_income_flag": False},
        confidence_score=0.9,
        contradictions_detected=False,
        contradiction_detail=None,
        dominant_signals=[],
        dismissed_signals=[],
        status="active",
        trace={}
    )
    
    severity = SeverityPrediction(
        severity_level=3,
        severity_label="Severe",
        affected_radius_km=2.0,
        affected_population=30000,
        estimated_duration_hours=10.0,
        peak_impact_time="2026-05-18T18:00:00Z",
        spread_risk=0.5,
        cascading_risks=[],
        uncertainty_range="",
        trace={}
    )
    
    allocation = AllocationPlan(
        plan_id="p-1",
        crisis_allocations=[],
        unmet_needs=[],
        trade_off_explanation="None",
        total_resources_deployed=10,
        estimated_cost_pkr=50000.0,
        fairness_check="Passed",
        trace={}
    )
    
    input_data = SimulationInput(
        crisis=crisis,
        severity=severity,
        allocation=allocation
    )
    
    # Mock Gemini
    agent.call_gemini = lambda prompt, fallback: ({
        "response_actions": [
            {
                "action_type": "evacuation",
                "description": "Evacuate low-lying areas in G-10",
                "estimated_completion_minutes": 45,
                "resources_involved": ["MOCK-RESCUE-1"],
                "expected_outcome": "300 people moved to safety",
                "side_effects": ["Traffic block on G-10 markaz road"]
            }
        ],
        "after_state": {
            "population_at_risk": 5000,
            "roads_blocked": ["G-10 Markaz Road"],
            "hospital_capacity_used_pct": 15.0,
            "estimated_casualties_if_unaddressed": 50,
            "response_coverage_pct": 85.0
        },
        "metrics": {
            "response_time_improvement_pct": 40.0,
            "population_protected": 25000,
            "roads_rerouted": 3,
            "estimated_cost_pkr": 45000.0,
            "estimated_lives_protected": 50
        },
        "baseline_comparison": {
            "baseline_response_time_minutes": 45.0,
            "amaan_response_time_minutes": 15.0,
            "baseline_false_positive_rate": 0.25,
            "amaan_false_positive_rate": 0.05,
            "baseline_resource_utilization_pct": 50.0,
            "amaan_resource_utilization_pct": 85.0,
            "improvement_summary": "Amaan improved response time by 30 mins."
        }
    }, False)
    
    output = await agent.run(input_data)
    
    assert isinstance(output, SimulationResult)
    assert len(output.response_actions) > 0
    assert output.baseline_comparison.amaan_response_time_minutes < output.baseline_comparison.baseline_response_time_minutes
    assert "trace" in output.model_dump()
