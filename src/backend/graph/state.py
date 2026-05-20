"""
CrisisState — Shared state schema for the CIRO LangGraph workflow.

All graph nodes read from and write to this state.
Modeled after SlashAgents' AgentState pattern.

Key design:
  - Every agent output gets its own key (no overwriting)
  - verification_debate tracks the reflection loop
  - demo_mode + api_failed control deterministic vs LLM routing
  - pipeline_status tracks overall pipeline health
"""

from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict


# ================================================================
# 1. VERIFICATION DEBATE STATE — Reflection Loop Tracking
# ================================================================
class VerificationDebateState(TypedDict):
    """
    Tracks the Classification ⇄ Verification reflection loop.
    Similar to SlashAgents' InvestDebateState for Bull/Bear debate.
    """
    classification_history: Annotated[str, "Previous classification reasoning"]
    verification_history: Annotated[str, "Previous verification reasoning"]
    critique: Annotated[str, "Critique from VerificationAgent for re-classification"]
    iteration_count: Annotated[int, "Number of reflection loop iterations (max 2)"]
    resolved: Annotated[bool, "Whether the contradiction has been resolved"]


# ================================================================
# 2. CRISIS STATE — Main Graph State (Shared Across All Nodes)
# ================================================================
class CrisisState(TypedDict):
    """
    Main state flowing through the CIRO LangGraph.

    Replaces the manual data passing in orchestrator.py.
    Each agent node reads its inputs from state keys and writes
    its outputs to designated state keys.
    """

    # ── CORE INPUT CONTEXT ──
    location: Annotated[Dict[str, Any], "Crisis location: {lat, lng, city, sector, address}"]
    radius_km: Annotated[float, "Search radius in kilometers"]
    time_window_hours: Annotated[int, "Signal lookback window in hours"]

    # ── CONTROL FLAGS ──
    demo_mode: Annotated[bool, "If True, force deterministic routing (no LLM supervisor)"]
    api_failed: Annotated[bool, "If True, at least one API tool failed — use fallback mode"]

    # ── SIGNAL INGESTION OUTPUT ──
    raw_signals: Annotated[List[Dict], "Normalized signals from SignalIngestionAgent"]
    ingestion_sources_contacted: Annotated[List[str], "APIs that responded successfully"]
    ingestion_sources_failed: Annotated[List[str], "APIs that failed"]
    ingestion_fallback_used: Annotated[bool, "Whether mock data was used as fallback"]
    ingestion_trace: Annotated[Dict, "SignalIngestionAgent trace for judges"]

    # ── CRISIS CLASSIFICATION OUTPUT ──
    crisis_object: Annotated[Optional[Dict], "Primary CrisisObject from ClassificationAgent"]
    secondary_crisis: Annotated[Optional[Dict], "Secondary crisis (for dual-crisis scenarios)"]
    classification_method: Annotated[str, "gemini_inference or rule_based_fallback"]
    classification_trace: Annotated[Dict, "CrisisClassificationAgent trace"]

    # ── VULNERABILITY / HISTORICAL DATA ──
    vulnerability_data: Annotated[Dict, "ICT sector vulnerability data from ict_vulnerability.json"]
    weather_data: Annotated[Dict, "Extracted weather metrics for severity calculation"]

    # ── SEVERITY PREDICTION OUTPUT ──
    severity_prediction: Annotated[Optional[Dict], "SeverityPrediction from SeverityAgent"]
    severity_trace: Annotated[Dict, "SeverityPredictionAgent trace"]

    # ── RESOURCE ALLOCATION OUTPUT ──
    allocation_plan: Annotated[Optional[Dict], "AllocationPlan from ResourceAllocationAgent"]
    allocation_trace: Annotated[Dict, "ResourceAllocationAgent trace"]

    # ── SIMULATION OUTPUT ──
    simulation_result: Annotated[Optional[Dict], "SimulationResult from SimulationAgent"]
    simulation_trace: Annotated[Dict, "SimulationAgent trace"]

    # ── STAKEHOLDER COMMS OUTPUT ──
    comms_output: Annotated[Optional[Dict], "StakeholderCommsOutput"]
    comms_trace: Annotated[Dict, "StakeholderCommsAgent trace"]

    # ── VERIFICATION OUTPUT ──
    verification_output: Annotated[Optional[Dict], "VerificationOutput"]
    verification_trace: Annotated[Dict, "VerificationAgent trace"]

    # ── REFLECTION LOOP STATE ──
    verification_debate: Annotated[
        VerificationDebateState,
        "Classification ⇄ Verification reflection loop state"
    ]

    # ── PIPELINE METADATA ──
    event_id: Annotated[str, "Unique pipeline run ID"]
    agents_executed: Annotated[List[str], "Ordered list of agents that ran"]
    trace_summary: Annotated[List[str], "Human-readable summary of each agent's output"]
    pipeline_status: Annotated[str, "running | completed | retracted | degraded | idle | monitoring"]
    total_latency_ms: Annotated[float, "Total pipeline execution time in milliseconds"]
