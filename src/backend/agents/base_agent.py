"""
BaseAgent — Foundation class for all 8 Amaan agents.
Provides Groq client (replacing Gemini for dev), Firestore logging, and trace generation.
Every agent inherits this — never duplicate these methods.
"""

import os
import json
from datetime import datetime, timezone
from groq import Groq

# Data directory path — works both locally and in Docker
def _find_dir(name: str) -> str:
    """Find a directory by walking up from this file."""
    docker_path = os.path.join("/app", name)
    if os.path.isdir(docker_path):
        return docker_path
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        candidate = os.path.join(current, name)
        if os.path.isdir(candidate):
            return candidate
        current = os.path.dirname(current)
    return os.path.join(os.getcwd(), name)

DATA_DIR = _find_dir("data")
SUBMISSION_DIR = _find_dir("submission")


class BaseAgent:
    """
    Base class for all Amaan agents.
    Provides Groq client, Firestore logging, and trace generation.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        # Using Llama 3.3 70B — Groq's most powerful and fastest model
        self.model_name = "llama-3.3-70b-versatile"

        # Create Groq Client
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

        self.db = None
        try:
            from firebase_admin import firestore
            self.db = firestore.client()
        except Exception:
            try:
                import firebase_admin
                from firebase_admin import credentials
                firebase_admin.initialize_app()
                from firebase_admin import firestore
                self.db = firestore.client()
            except Exception:
                # Firestore unavailable — use file-based trace persistence
                self.db = None

    def call_gemini(self, prompt: str, fallback: dict) -> tuple[dict, bool]:
        """
        Call Groq API (Kept the name 'call_gemini' so other agent files don't break).
        Returns parsed JSON dict + fallback_triggered boolean.
        """
        if not self.client:
            print(f"[{self.agent_name}] No GROQ_API_KEY configured. Using fallback.")
            return fallback, True

        # Groq's JSON mode strictly requires the word "JSON" in the prompt
        if "json" not in prompt.lower():
            prompt += "\n\nYou MUST return your response entirely in valid JSON format."

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                response_format={"type": "json_object"},
                temperature=0.2, # Low temp for deterministic JSON
                timeout=30.0,
            )
            
            response_text = response.choices[0].message.content
            return json.loads(response_text), False
            
        except Exception as e:
            print(f"[{self.agent_name}] Groq failed: {e}. Using fallback.")
            return fallback, True

    def log_trace(
        self,
        trace_id: str,
        input_data: dict,
        reasoning_steps: list[str],
        confidence_score: float,
        decision_made: dict,
        alternative_considered: str | None,
        fallback_triggered: bool
    ) -> dict:
        """
        Logs every agent decision to Firestore agent_traces collection.
        """
        trace = {
            "trace_id": trace_id,
            "agent": self.agent_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_data": input_data,
            "reasoning_steps": reasoning_steps,
            "confidence_score": round(confidence_score, 3),
            "decision_made": decision_made,
            "alternative_considered": alternative_considered,
            "fallback_triggered": fallback_triggered
        }

        if self.db:
            try:
                self.db.collection("agent_traces").document(trace_id).set(trace)
            except Exception as e:
                print(f"Warning: Failed to save trace to Firestore: {e}")
                self._save_trace_to_file(trace)
        else:
            self._save_trace_to_file(trace)

        return trace

    def _save_trace_to_file(self, trace: dict):
        """Fallback persistence — save traces to JSON file for export."""
        trace_file = os.path.join(SUBMISSION_DIR, "amaan_agent_traces.json")
        os.makedirs(os.path.dirname(trace_file), exist_ok=True)

        traces = []
        if os.path.exists(trace_file):
            try:
                with open(trace_file, 'r') as f:
                    traces = json.load(f)
            except Exception:
                pass

        traces.append(trace)
        with open(trace_file, 'w') as f:
            json.dump(traces, f, indent=2)