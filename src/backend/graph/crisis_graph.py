"""
CIROCrisisGraph — Top-level crisis graph orchestrator.

Replaces AmaanOrchestrator with a LangGraph-based pipeline.
Mirrors SlashAgents' SlashAgentsCryptoGraph pattern.

Usage:
    graph = CIROCrisisGraph(demo_mode=True)
    result = await graph.run_pipeline(location={"lat": 33.7, "lng": 73.0, ...})
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from graph.builder import CIROGraphBuilder
from graph.edges import CIROEdges
from graph.propagation import CIROPropagator
from graph.reflection import CIROReflector

logger = logging.getLogger(__name__)


class CIROCrisisGraph:
    """
    Top-level crisis graph orchestrator.
    Replaces AmaanOrchestrator with LangGraph StateGraph.
    """

    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.edges = CIROEdges()
        self.builder = CIROGraphBuilder(self.edges)
        self.propagator = CIROPropagator()
        self.reflector = CIROReflector()
        self.graph = self.builder.build()

        # State tracking (for post-run analysis)
        self.last_state: Optional[Dict[str, Any]] = None
        self.run_history: list = []

        logger.info(f"[CIROGraph] Initialized (demo_mode={demo_mode})")

    async def run_pipeline(
        self,
        location: dict,
        radius_km: float = 10.0,
        time_window_hours: int = 2,
    ) -> Dict[str, Any]:
        """
        Run the full crisis detection and response pipeline.

        Args:
            location: Crisis location dict with lat, lng, city, sector
            radius_km: Signal search radius
            time_window_hours: Signal lookback window

        Returns:
            Final CrisisState dict with all agent outputs
        """
        start_time = time.time()

        # Create initial state
        init_state = self.propagator.create_initial_state(
            location=location,
            radius_km=radius_km,
            time_window_hours=time_window_hours,
            demo_mode=self.demo_mode,
        )

        # Run the graph
        config = self.propagator.get_graph_config()
        try:
            final_state = await self.graph.ainvoke(init_state, config=config)
        except Exception as e:
            logger.error(f"[CIROGraph] Graph execution failed: {e}")
            final_state = {
                **init_state,
                "pipeline_status": "degraded",
                "trace_summary": init_state.get("trace_summary", []) + [
                    f"Pipeline failed: {str(e)}"
                ],
            }

        # Calculate latency
        elapsed_ms = (time.time() - start_time) * 1000
        final_state["total_latency_ms"] = round(elapsed_ms, 1)

        # Extract lesson from reflection loop
        lesson = self.reflector.extract_lesson(final_state)
        if lesson:
            final_state["trace_summary"] = final_state.get("trace_summary", []) + [
                f"Reflection: {lesson}"
            ]

        # Track state
        self.last_state = final_state
        self.run_history.append({
            "event_id": final_state.get("event_id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": final_state.get("pipeline_status"),
            "latency_ms": elapsed_ms,
            "agents_executed": final_state.get("agents_executed", []),
        })

        logger.info(
            f"[CIROGraph] Pipeline completed: status={final_state.get('pipeline_status')}, "
            f"latency={elapsed_ms:.0f}ms, agents={len(final_state.get('agents_executed', []))}"
        )

        return final_state

    def to_api_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert final CrisisState to API response format.
        Matches the existing OrchestratorResponse contract.
        """
        pipeline_status = state.get("pipeline_status", "completed")
        crisis_detected = pipeline_status == "completed" and state.get("crisis_object") is not None

        response = {
            "event_id": state.get("event_id", ""),
            "crisis_detected": crisis_detected,
            "status": pipeline_status,
            "trace_summary": state.get("trace_summary", []),
            "agents_executed": state.get("agents_executed", []),
            "total_latency_ms": state.get("total_latency_ms", 0),
        }

        if crisis_detected:
            response["final_output"] = {
                "crisis": state.get("crisis_object"),
                "severity": state.get("severity_prediction"),
                "allocation": state.get("allocation_plan"),
                "simulation": state.get("simulation_result"),
                "comms": state.get("comms_output"),
            }
        elif pipeline_status == "retracted":
            response["final_output"] = {
                "verification": state.get("verification_output"),
                "correction_messages": (
                    state.get("verification_output", {}).get("correction_messages", [])
                ),
            }

        return response
