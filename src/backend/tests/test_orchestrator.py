import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.orchestrator import AmaanOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_end_to_end():
    # Setup mock data to ensure all APIs fall back to demo data in Scenario A
    os.environ["DEMO_MODE"] = "1"
    
    orchestrator = AmaanOrchestrator()
    
    # We run it for G-10 Islamabad (Scenario A)
    location = {"lat": 33.70, "lng": 73.00, "sector": "G-10"}
    
    # Mocking Gemini for all agents might be tricky, but since they all have fallbacks,
    # let's just let the fallbacks run or mock the call_gemini for each agent.
    # Actually, the base agent's try/except will automatically fallback if API key is invalid/missing.
    
    response = await orchestrator.run_pipeline(location=location)
    
    assert response.crisis_detected is True
    assert response.status == "active_response"
    assert len(response.trace_summary) >= 6 # One for each agent in the chain
    
    assert "final_output" in response.model_dump()
    final_output = response.final_output
    assert "crisis" in final_output
    assert "allocation" in final_output
    assert "comms" in final_output
