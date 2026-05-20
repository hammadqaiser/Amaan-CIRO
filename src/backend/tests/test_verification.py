import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.verification import VerificationAgent
from src.backend.models.schemas import (
    VerificationInput, CrisisObject, RawSignal, VerificationOutput
)

@pytest.mark.asyncio
async def test_verification_agent_retraction():
    agent = VerificationAgent()
    
    # Mock dependencies
    crisis = CrisisObject(
        crisis_id="1", crisis_type="urban_flood", sub_type="flash",
        location={"lat": 33.7, "lng": 73.0, "sector": "G-10"},
        confidence_score=0.45,  # Unverified
        contradictions_detected=True, contradiction_detail="Conflicting reports",
        dominant_signals=[], dismissed_signals=[], status="unverified", trace={}
    )
    
    new_signals = [
        RawSignal(
            signal_id="ns-1",
            source="citizen_app",
            signal_type="field_report",
            content="Field report confirmed it's just a burst water main, not a flood. Controlled.",
            location={"lat": 33.7, "lng": 73.0},
            timestamp="2026-05-18T12:00:00Z",
            credibility_score=0.90,
            staleness_flag=False,
            raw_data={}
        )
    ]
    
    input_data = VerificationInput(
        crisis=crisis,
        new_signals=new_signals,
        original_classification_trace={"reasoning_steps": ["Low confidence due to contradiction"]},
        trigger_mode="manual"
    )
    
    # Mock Gemini
    agent.call_gemini = lambda prompt, fallback: ({
        "verdict": "retracted",
        "retraction_reason": "New field report confirmed it is a burst water main, not an urban flood.",
        "correction_messages": ["Please disregard previous flood warning. It is a burst water main and is controlled."],
        "confidence_delta": -0.45
    }, False)
    
    output = await agent.run(input_data)
    
    assert isinstance(output, VerificationOutput)
    assert output.verdict == "retracted"
    assert output.updated_crisis.status == "retracted"
    assert output.updated_crisis.confidence_score == 0.0
    assert "trace" in output.model_dump()
