"""
Propagation — Initial state factory for the CIRO crisis graph.
Mirrors SlashAgents' graph/propagation.py pattern.

Creates the initial CrisisState with all fields initialized to safe defaults.
"""

import uuid
from typing import Dict, Any


class CIROPropagator:
    """Creates initial state for graph invocation."""

    def __init__(self, max_recur_limit: int = 25):
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self,
        location: dict,
        radius_km: float = 10.0,
        time_window_hours: int = 2,
        demo_mode: bool = False,
    ) -> Dict[str, Any]:
        """Create the initial CrisisState for the graph."""
        return {
            # ── Core input ──
            "location": location,
            "radius_km": radius_km,
            "time_window_hours": time_window_hours,
            # ── Control flags ──
            "demo_mode": demo_mode,
            "api_failed": False,
            # ── Ingestion output ──
            "raw_signals": [],
            "ingestion_sources_contacted": [],
            "ingestion_sources_failed": [],
            "ingestion_fallback_used": False,
            "ingestion_trace": {},
            # ── Classification output ──
            "crisis_object": None,
            "secondary_crisis": None,
            "classification_method": "",
            "classification_trace": {},
            # ── Context data ──
            "vulnerability_data": {},
            "weather_data": {},
            # ── Severity output ──
            "severity_prediction": None,
            "severity_trace": {},
            # ── Allocation output ──
            "allocation_plan": None,
            "allocation_trace": {},
            # ── Simulation output ──
            "simulation_result": None,
            "simulation_trace": {},
            # ── Comms output ──
            "comms_output": None,
            "comms_trace": {},
            # ── Verification output ──
            "verification_output": None,
            "verification_trace": {},
            # ── Reflection loop ──
            "verification_debate": {
                "classification_history": "",
                "verification_history": "",
                "critique": "",
                "iteration_count": 0,
                "resolved": False,
            },
            # ── Pipeline metadata ──
            "event_id": str(uuid.uuid4()),
            "agents_executed": [],
            "trace_summary": [],
            "pipeline_status": "running",
            "total_latency_ms": 0.0,
        }

    def get_graph_config(self) -> Dict[str, Any]:
        """Config passed when invoking the LangGraph."""
        return {
            "recursion_limit": self.max_recur_limit,
        }
