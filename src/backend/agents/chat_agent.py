"""
ChatAgent — Multilingual citizen-facing Q&A about nearby dangers.
Build order: Last — independent pipeline.
Evaluation relevance: Usability & UX 10%.

Runs completely independently of the crisis pipeline.
Answers citizen questions in Urdu, Roman Urdu, or English.
Uses current crisis state from in-memory store as real-time context.
Also has deep knowledge of the Amaan CIRO system for judge questions.
"""

import uuid
import json
import re

from agents.base_agent import BaseAgent
from models.schemas import ChatInput, ChatOutput

CHAT_SYSTEM_PROMPT = """
You are Amaan Assistant — the AI chatbot for Pakistan's first AI-powered crisis detection and response system called Amaan CIRO (Crisis Intelligence & Response Orchestrator).

═══ SYSTEM ARCHITECTURE KNOWLEDGE ═══

Amaan CIRO is built with 8 specialized AI agents running on a FastAPI backend deployed to Google Cloud Run:

1. **SignalIngestionAgent** — Fetches real-time data from Open-Meteo (weather/rainfall), Google Traffic (congestion), GDELT Project (news/social), and Citizen App field reports. Applies credibility scoring (0.0–1.0) and staleness rules (signals older than 2 hours get flagged).

2. **CrisisClassificationAgent** — Receives normalized signals and classifies the crisis type (urban_flood, heatwave, accident, power_outage, infrastructure, compound). Uses Gemini/Groq LLM with a rule-based keyword fallback. Detects signal contradictions.

3. **SeverityPredictionAgent** — Predicts severity level (1-Minor to 5-Catastrophic), affected population, geographic spread, estimated duration, and cascading risks. Uses NDMA vulnerability data for Islamabad sectors.

4. **ResourceAllocationAgent** — Optimizes allocation of constrained emergency resources (ambulances, rescue boats, rescue teams, police units, medical outreach, water tankers, generators, shelters) across simultaneous crises. Applies a 15% fairness bonus for low-income areas (I-8, I-10).

5. **SimulationAgent** — Models before/after states for response actions: population at risk reduction, road clearance, hospital capacity management. Shows what would happen without vs. with Amaan's response.

6. **StakeholderCommsAgent** — Generates bilingual (English + Urdu) messages for 5 audience types: NDMA Command, Emergency Services (Rescue 1122), Hospitals (PIMS), Public Citizens, and Media/Press.

7. **VerificationAgent** — Handles contradictions, false alarms, and crisis retractions. Triggered when classification confidence < 0.50. Can retract a crisis and issue correction messages.

8. **ChatAgent** (you) — Multilingual citizen-facing Q&A. Answers questions in English, Urdu, or Roman Urdu about nearby dangers, shelters, and safety actions.

The agents run in sequence: Signal Ingestion → Classification → [Verification if low confidence] → Severity Prediction → Resource Allocation → Simulation → Stakeholder Communications.

═══ MAP & DASHBOARD KNOWLEDGE ═══

The interactive map dashboard has these visual layers (users can toggle each):
- **Crisis Zones**: Red/blue animated circles showing active crisis epicenters with pulsing ⚠️ markers. Blue = flood, Amber = heatwave.
- **Weather Radar**: Simulated Doppler precipitation layers — red (heavy rain), amber (moderate), green (light) concentric circles around flood crises.
- **Resources**: Emergency fleet stations marked with 🏢 icons. When dispatched, dashed lines show routes from station to crisis. Ambulances (🚑), Rescue Teams (⛵), and unit IDs like AMB-01, BOAT-01, TEAM-01.
- **Shelters**: Green 🏠 markers showing emergency shelters with capacity bars. Three shelters: G-10 Markaz Community Center (300 capacity), I-8 Government School (200 capacity), Rawalpindi Sports Complex (500 capacity).
- **Vulnerability**: Color-coded sector risk badges. G-10 (85% risk, red), G-11 (80%), G-13 (78%), I-10 (72%), I-8 (60%, amber), F-6 (30%, green), F-7 (25%, green). Clicking shows drainage capacity, population density, and historical flood count.
- **Field Signals**: Small pulsing icons showing active signal sources — 🌧️ for weather, 🚗 for traffic, 📰 for news, 👥 for citizen reports. Each shows credibility score and staleness status on hover.
- **Evacuation Routes**: Green dashed lines from crisis epicenter to nearest shelter.
- **Dispatch Lines**: Dashed polylines from resource stations to crisis locations showing tactical routes.

The dashboard also has panels for: System Overview, Stakeholder Communications (5 audience tabs), Resource Allocation details, Simulation Results (before/after comparison), and a Tactical Fleet Inventory.

═══ DEMO SCENARIOS ═══

Scenario A (Primary Demo): G-10 Islamabad urban flooding. 82mm rainfall in 3 hours, severe traffic congestion on Jinnah Avenue, water entering basements. One contradicting signal (water main burst) gets dismissed due to staleness. Resources deployed: rescue boats, rescue teams, ambulances. Traffic rerouted. Bilingual public alert sent.

Scenario B (False Alarm): Low-confidence flood signal in G-10. Field verification confirms it's a water main burst, not a flood. Crisis retracted. Stand-down orders sent. Demonstrates robustness.

Scenario C (Dual Crisis): Simultaneous G-10 flooding (Severity 4) + I-8 heatwave (Severity 2). System shows resource trade-off with 15% fairness bonus for I-8 low-income area. Split deployment.

═══ ACTIVE CRISIS CONTEXT ═══

Active crises near this user right now:
{active_crises_json}

Current weather at user location:
{weather_json}

Nearest shelters:
{shelters_json}

═══ RESPONSE RULES ═══

- Respond in the same language the user wrote in
- If the user writes Urdu script (اردو characters) → respond in Urdu script
- If the user writes Roman Urdu (e.g. "kya hal hai") → respond in Roman Urdu
- If the user writes English → respond in English
- If the user writes mixed → respond in Roman Urdu (most accessible for Pakistan)
- Keep responses under 150 words
- If any danger is nearby, always state what the user should do immediately
- Use the system architecture knowledge to answer questions about Amaan, the map, agents, or how the system works
- If you don't know something, say so clearly and give the 1122 helpline
- Be calm and factual — never cause panic
- If user asks about traffic, check crisis data for road blockages first
- Always end with a specific action if any safety risk exists nearby
- When asked about the map, describe the specific layers and icons visible

Return ONLY this JSON:
{{
    "response": "string",
    "language_detected": "string",
    "crisis_context_used": true or false,
    "nearby_crises": ["crisis_id strings"],
    "safety_actions": ["specific action strings"]
}}
"""

# In-memory reference to active crises (set by main.py)
_active_crises_store = []
_shelters_store = []
_weather_store = {}


def set_active_crises(crises: list):
    """Called by main.py to update the chat agent's crisis context."""
    global _active_crises_store
    _active_crises_store = crises


def set_shelters(shelters: list):
    """Called by main.py to update the chat agent's shelter context."""
    global _shelters_store
    _shelters_store = shelters


def set_weather_context(weather_data: dict):
    """Called by main.py to update the chat agent's weather context."""
    global _weather_store
    _weather_store = weather_data


class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="ChatAgent")

    def _detect_language(self, text: str) -> str:
        """Detect language from user input text."""
        # Check for Urdu script characters
        urdu_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')
        if urdu_pattern.search(text):
            return "urdu"

        # Check for Roman Urdu patterns
        roman_urdu_words = [
            "kya", "hai", "kahan", "koi", "abhi", "mein", "hain", "aaj",
            "yahan", "wahan", "nahi", "haan", "jee", "bhai", "ap", "apka",
            "kaise", "kitna", "kidhar", "udhar", "chalein", "janab",
            "salam", "assalam", "walaikum", "mashallah", "inshallah"
        ]
        text_lower = text.lower()
        roman_urdu_count = sum(1 for w in roman_urdu_words if w in text_lower)
        if roman_urdu_count >= 2:
            return "roman_urdu"

        return "english"

    def _get_crisis_context(self) -> tuple[str, str, str]:
        """Build crisis context strings from active state."""
        if _active_crises_store:
            crises_json = json.dumps(_active_crises_store, indent=2, default=str)
        else:
            crises_json = json.dumps([
                {"type": "No active crises detected", "status": "monitoring"}
            ])

        if _shelters_store:
            shelters_json = json.dumps(_shelters_store, indent=2, default=str)
        else:
            shelters_json = json.dumps([
                {"name": "G-10 Markaz Community Center", "address": "G-10 Markaz, Islamabad", "capacity": 300},
                {"name": "I-8 Government School", "address": "I-8/2, Islamabad", "capacity": 200}
            ])

        if _weather_store:
            weather_json = json.dumps(_weather_store, indent=2, default=str)
        else:
            weather_json = json.dumps({"status": "Live weather data not available in chat context"})

        return crises_json, weather_json, shelters_json

    def _get_fallback_response(self, msg: str, language: str) -> dict:
        """Generate fallback response when Gemini is unavailable."""
        crisis_ids = [c.get("crisis_id", "") for c in _active_crises_store if isinstance(c, dict)]

        if language == "urdu":
            response = (
                "ابھی کوئی فوری خطرہ نہیں ہے۔ "
                "اگر آپ کو ایمرجنسی ہے تو 1122 پر کال کریں۔"
            )
        elif language == "roman_urdu":
            response = (
                "Abhi koi fori khatra nahi hai. "
                "Agar aap ko emergency hai to 1122 pe call karein."
            )
        else:
            response = (
                "No immediate danger detected in your area. "
                "If this is an emergency, please call 1122 immediately."
            )

        if _active_crises_store:
            # Build a richer fallback using actual crisis data
            crisis_types = [c.get("crisis_type", "unknown") for c in _active_crises_store if isinstance(c, dict)]
            crisis_locations = [c.get("location", {}).get("sector", c.get("location", {}).get("city", "Islamabad")) for c in _active_crises_store if isinstance(c, dict)]

            if language == "english":
                crisis_desc = ", ".join([f"{t.replace('_', ' ')} in {l}" for t, l in zip(crisis_types, crisis_locations)])
                response = (
                    f"⚠️ ACTIVE ALERT: {len(_active_crises_store)} crisis/crises detected near you: {crisis_desc}. "
                    f"Stay alert, follow official instructions, and avoid affected areas. "
                    f"Nearest shelter: G-10 Markaz Community Center. Helpline: 1122."
                )
            elif language == "roman_urdu":
                response = (
                    f"⚠️ ALERT: Aap ke qareeb {len(_active_crises_store)} crisis/crises hain. "
                    f"Hoshyar rahein, official hidayaat follow karein aur mutasira ilaqon se door rahein. "
                    f"Qareeb tareen shelter: G-10 Markaz Community Center. Helpline: 1122."
                )
            elif language == "urdu":
                response = (
                    f"⚠️ الرٹ: آپ کے قریب {len(_active_crises_store)} بحران ہے۔ "
                    f"ہوشیار رہیں اور سرکاری ہدایات پر عمل کریں۔ "
                    f"قریب ترین شیلٹر: جی-۱۰ مارکز کمیونٹی سینٹر۔ ہیلپ لائن: 1122۔"
                )

        # Check if the user is asking about the system/map (for judges)
        msg_lower = msg.lower()
        system_questions = ["what is amaan", "what is ciro", "how does", "tell me about", "explain",
                          "what agents", "how many agents", "map", "architecture", "dashboard"]
        if any(kw in msg_lower for kw in system_questions) and language == "english":
            response = (
                "Amaan CIRO is Pakistan's first AI-powered crisis detection system with 8 specialized agents: "
                "Signal Ingestion, Crisis Classification, Severity Prediction, Resource Allocation, Simulation, "
                "Stakeholder Communications, Verification, and Chat (me). "
                "The map shows crisis zones, weather radar, shelters, fleet resources, vulnerability sectors, "
                "and live field signals. Ask me anything specific about these features!"
            )
            return {
                "response": response,
                "language_detected": language,
                "crisis_context_used": False,
                "nearby_crises": crisis_ids,
                "safety_actions": ["Explore the dashboard to see all layers"]
            }

        return {
            "response": response,
            "language_detected": language,
            "crisis_context_used": bool(_active_crises_store),
            "nearby_crises": crisis_ids,
            "safety_actions": ["Call 1122 for emergencies"]
        }

    async def run(self, input_data: ChatInput) -> ChatOutput:
        """Execute chat response pipeline."""
        reasoning_steps = []

        # Detect language
        if input_data.language_preference == "auto":
            language = self._detect_language(input_data.user_message)
        else:
            language = input_data.language_preference
        reasoning_steps.append(f"Language detected: {language}")

        # Get crisis context
        crises_json, weather_json, shelters_json = self._get_crisis_context()
        reasoning_steps.append(f"Active crises in context: {len(_active_crises_store)}")

        # Build prompt
        prompt = CHAT_SYSTEM_PROMPT.format(
            active_crises_json=crises_json,
            weather_json=weather_json,
            shelters_json=shelters_json
        )
        # Add the user's actual message
        full_prompt = f"{prompt}\n\nUser message: {input_data.user_message}"

        # Add conversation history for context
        if input_data.conversation_history:
            history_text = "\n".join([
                f"{'User' if i % 2 == 0 else 'Amaan'}: {msg}"
                for i, msg in enumerate(input_data.conversation_history[-6:])
            ])
            full_prompt = f"{prompt}\n\nRecent conversation:\n{history_text}\n\nUser message: {input_data.user_message}"

        fallback = self._get_fallback_response(input_data.user_message, language)
        gemini_out, fallback_triggered = self.call_gemini(full_prompt, fallback)

        if fallback_triggered:
            reasoning_steps.append("Used fallback response (Gemini unavailable)")
        else:
            reasoning_steps.append("Generated response via Gemini LLM")

        trace_id = str(uuid.uuid4())
        trace = self.log_trace(
            trace_id=trace_id,
            input_data={
                "user_message": input_data.user_message,
                "language": language,
                "location": input_data.user_location
            },
            reasoning_steps=reasoning_steps,
            confidence_score=0.85,
            decision_made={"language": gemini_out.get("language_detected", language)},
            alternative_considered="Multilingual fallback responses",
            fallback_triggered=fallback_triggered
        )

        return ChatOutput(
            response=gemini_out.get("response", fallback["response"]),
            language_detected=gemini_out.get("language_detected", language),
            crisis_context_used=gemini_out.get("crisis_context_used", fallback["crisis_context_used"]),
            nearby_crises=gemini_out.get("nearby_crises", fallback["nearby_crises"]),
            safety_actions=gemini_out.get("safety_actions", fallback["safety_actions"]),
            trace=trace
        )
