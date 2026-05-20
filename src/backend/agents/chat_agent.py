"""
ChatAgent — Multilingual citizen-facing Q&A about nearby dangers.
Build order: Last — independent pipeline.
Evaluation relevance: Usability & UX 10%.

Runs completely independently of the crisis pipeline.
Answers citizen questions in Urdu, Roman Urdu, or English.
Uses current crisis state from in-memory store as real-time context.
"""

import uuid
import json
import re

from agents.base_agent import BaseAgent
from models.schemas import ChatInput, ChatOutput

CHAT_SYSTEM_PROMPT = """
You are Amaan Assistant, a crisis safety chatbot for Pakistan.
You help citizens understand nearby dangers and stay safe.

Active crises near this user right now:
{active_crises_json}

Current weather at user location:
{weather_json}

Nearest shelters:
{shelters_json}

Rules you must follow:
- Respond in the same language the user wrote in
- If the user writes Urdu script (اردو characters) → respond in Urdu script
- If the user writes Roman Urdu (e.g. "kya hal hai") → respond in Roman Urdu
- If the user writes English → respond in English
- If the user writes mixed → respond in Roman Urdu (most accessible for Pakistan)
- Keep responses under 100 words
- If any danger is nearby, always state what the user should do immediately
- Only use information provided above — never invent facts
- If you don't know something, say so clearly and give the 1122 helpline
- Be calm and factual — never cause panic
- If user asks about traffic, check crisis data for road blockages first
- Always end with a specific action if any safety risk exists nearby

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


def set_active_crises(crises: list):
    """Called by main.py to update the chat agent's crisis context."""
    global _active_crises_store
    _active_crises_store = crises


def set_shelters(shelters: list):
    """Called by main.py to update the chat agent's shelter context."""
    global _shelters_store
    _shelters_store = shelters


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
            if language == "english":
                response = (
                    f"There are {len(_active_crises_store)} active alerts near you. "
                    f"Stay alert and follow official instructions. Helpline: 1122."
                )
            elif language == "roman_urdu":
                response = (
                    f"Aap ke qareeb {len(_active_crises_store)} alerts hain. "
                    f"Hoshyar rahein aur official hidayaat follow karein. Helpline: 1122."
                )

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
