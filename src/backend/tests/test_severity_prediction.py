import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.severity_prediction import SeverityPredictionAgent
from src.backend.models.schemas import SeverityPredictionInput, CrisisObject, SeverityPrediction

@pytest.mark.asyncio
async def test_severity_prediction_calculations():
    agent = SeverityPredictionAgent()
    
    # Mocking G-10 vulnerability from data/ict_vulnerability.json
    vulnerability_data = {
        "flood_vulnerability": 0.85,
        "drainage_capacity_mm_per_hr": 12,
        "population_density_per_sqkm": 8500,
        "low_income_flag": False
    }
    
    # 82mm rainfall in 3 hours = 27.33 mm/hr
    weather_data = {
        "rainfall_mm": 82.0,
        "rainfall_intensity_mm_per_hr": 27.33
    }
    
    crisis = CrisisObject(
        crisis_id="test-crisis",
        crisis_type="urban_flood",
        sub_type="flash_flood",
        location={"lat": 33.7047, "lng": 73.0079},
        confidence_score=0.82,
        contradictions_detected=False,
        contradiction_detail=None,
        dominant_signals=[],
        dismissed_signals=[],
        status="active",
        trace={}
    )
    
    input_data = SeverityPredictionInput(
        crisis=crisis,
        weather_data=weather_data,
        vulnerability_data=vulnerability_data,
        historical_events=[]
    )
    
    # For G-10 and radius ~1.4 km (let's say we set radius dynamically or fixed base for tests)
    output = await agent.run(input_data)
    
    assert isinstance(output, SeverityPrediction)
    
    # Check duration: (82.0 / 12) * 1.3 = 8.88 hours
    assert abs(output.estimated_duration_hours - 8.88) < 0.1
    
    # Check severity labels
    assert output.severity_level in [1, 2, 3, 4, 5]
    assert output.severity_label in ["Minor", "Moderate", "Severe", "Critical", "Catastrophic"]
    
    assert "trace" in output.model_dump()
