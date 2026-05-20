import pytest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.resource_allocation import ResourceAllocationAgent
from src.backend.models.schemas import (
    ResourceAllocationInput, 
    CrisisObject, 
    SeverityPrediction, 
    ResourceInventory, 
    AllocationConstraints
)

@pytest.mark.asyncio
async def test_resource_allocation_dual_crisis():
    agent = ResourceAllocationAgent()
    
    # Mock inventory
    from src.backend.agents.base_agent import DATA_DIR
    inv_file = os.path.join(DATA_DIR, "resource_inventory.json")
    with open(inv_file, "r") as f:
        inventory_data = json.load(f)
    inventory = ResourceInventory(**inventory_data)
    
    constraints = AllocationConstraints(
        budget_pkr=500000,
        max_travel_minutes=30,
        crew_shift_hours=8
    )
    
    # Crisis 1: Urban Flood, Severity 4, Low Income Area (I-10)
    flood_crisis = CrisisObject(
        crisis_id="c-flood",
        crisis_type="urban_flood",
        sub_type="flash_flood",
        location={"lat": 33.64, "lng": 73.04, "sector": "I-10", "low_income_flag": True},
        confidence_score=0.9,
        contradictions_detected=False,
        contradiction_detail=None,
        dominant_signals=[],
        dismissed_signals=[],
        status="active",
        trace={}
    )
    flood_sev = SeverityPrediction(
        severity_level=4,
        severity_label="Critical",
        affected_radius_km=2.0,
        affected_population=60000,
        estimated_duration_hours=10.0,
        peak_impact_time="2026-05-18T18:00:00Z",
        spread_risk=0.8,
        cascading_risks=[],
        uncertainty_range="",
        trace={}
    )
    
    # Crisis 2: Heatwave, Severity 3, Non-Low Income Area (G-10)
    heat_crisis = CrisisObject(
        crisis_id="c-heat",
        crisis_type="heatwave",
        sub_type="extreme_heat",
        location={"lat": 33.70, "lng": 73.00, "sector": "G-10", "low_income_flag": False},
        confidence_score=0.8,
        contradictions_detected=False,
        contradiction_detail=None,
        dominant_signals=[],
        dismissed_signals=[],
        status="active",
        trace={}
    )
    heat_sev = SeverityPrediction(
        severity_level=3,
        severity_label="Severe",
        affected_radius_km=3.0,
        affected_population=30000,
        estimated_duration_hours=48.0,
        peak_impact_time="2026-05-19T14:00:00Z",
        spread_risk=0.3,
        cascading_risks=[],
        uncertainty_range="",
        trace={}
    )
    
    input_data = ResourceAllocationInput(
        crises=[flood_crisis, heat_crisis],
        severity_predictions=[flood_sev, heat_sev],
        resource_inventory=inventory,
        constraints=constraints
    )
    
    # Mock Gemini call for trade-off explanation
    agent.call_gemini = lambda prompt, fallback: ({"explanation": "Mocked trade-off explanation: Insufficient resources to handle both simultaneously, prioritized flood."}, False)
    
    output = await agent.run(input_data)
    
    assert len(output.crisis_allocations) == 2
    
    # Flood should be ranked first due to higher impact score (severity 4 vs 3, population 60k vs 30k)
    assert output.crisis_allocations[0].crisis_id == "c-flood"
    
    # Flood severity 4 requires: 4 rescue boats, 4 rescue teams, 3 police units, 2 ambulances
    flood_alloc = output.crisis_allocations[0].resources_assigned
    assert flood_alloc.get("rescue_teams", 0) <= 4
    
    # Check trace
    assert "trace" in output.model_dump()
    assert "Impact score" in str(output.trace["reasoning_steps"])
