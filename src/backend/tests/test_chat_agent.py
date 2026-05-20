import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.agents.chat_agent import ChatAgent
from src.backend.models.schemas import ChatInput, ChatOutput

@pytest.mark.asyncio
async def test_chat_agent_roman_urdu():
    agent = ChatAgent()
    
    input_data = ChatInput(
        user_message="Yar yahan G-10 mein paani bohat zyada hai, kya karoon?",
        user_location={"lat": 33.7047, "lng": 73.0079},
        language_preference="Roman Urdu",
        conversation_history=[]
    )
    
    # Mock Gemini
    agent.call_gemini = lambda prompt, fallback: ({
        "response": "G-10 mein flood alert jari hai. Barae meharbani ghar ke andar rahen aur ground floor khali kar dein.",
        "language_detected": "Roman Urdu",
        "crisis_context_used": True,
        "nearby_crises": ["Urban Flood in G-10"],
        "safety_actions": ["Stay indoors", "Evacuate ground floor"]
    }, False)
    
    output = await agent.run(input_data)
    
    print("\n[DEBUG TEST] output type:", type(output), "id:", id(type(output)))
    print("[DEBUG TEST] ChatOutput in test:", ChatOutput, "id:", id(ChatOutput))
    assert isinstance(output, ChatOutput)
    assert output.language_detected == "Roman Urdu"
    assert output.crisis_context_used is True
    assert len(output.safety_actions) > 0
    assert "trace" in output.model_dump()
