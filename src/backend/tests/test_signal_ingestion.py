import pytest
import os
import sys
import json
from datetime import datetime, timedelta, timezone

# Add parent directory to path so src.backend... works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.signal_ingestion import SignalIngestionAgent
from src.backend.models.schemas import SignalIngestionInput, SignalIngestionOutput

@pytest.mark.asyncio
async def test_signal_ingestion_fallback_and_staleness():
    # Make sure we're in the right working directory to find data/
    original_cwd = os.getcwd()
    try:
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
        
        agent = SignalIngestionAgent()
        
        # We'll use G-10 Islamabad which is our primary test scenario
        input_data = SignalIngestionInput(
            location={"lat": 33.7047, "lng": 73.0079, "city": "Islamabad", "address": "G-10"},
            radius_km=10.0,
            time_window_hours=2
        )
        
        output = await agent.run(input_data)
        
        assert isinstance(output, SignalIngestionOutput)
        assert len(output.signals) > 0
        
        # If API fails, it will load the demo_scenarios.json fallback
        if output.fallback_used:
            assert "mock" not in output.sources_failed  # Fallback shouldn't fail
            
            # The citizen_app signal in demo_scenarios.json is dated 2026-05-18T10:00:00Z
            # Let's see if staleness is flagged. 
            citizen_signal = next((s for s in output.signals if s.source == "citizen_app"), None)
            if citizen_signal:
                # The credibility should have been reduced by 0.30 from 0.70
                assert citizen_signal.credibility_score <= 0.40
                
        # Validate trace presence
        assert "trace" in output.dict()
        assert output.trace["agent"] == "SignalIngestionAgent"
    finally:
        os.chdir(original_cwd)
