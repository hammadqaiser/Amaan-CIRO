# Data Flows & Orchestration

This document outlines the system data flow, orchestrator execution sequence, and API endpoint reference for the Amaan CIRO system.

## Orchestrator Pipeline

The orchestrator chains all agents in the correct sequence within the FastAPI backend process. It supports two execution modes: a direct Python orchestrator class and a LangGraph StateGraph topology.

### Execution Order

```
SignalIngestionAgent
        ↓
CrisisClassificationAgent
        ↓
    [confidence check]
        ├─ confidence < 0.50 → VerificationAgent (immediate mode)
        │       ├─ verified → continue pipeline
        │       └─ retracted → END, send retraction notifications
        └─ confidence >= 0.50 → continue
        ↓
SeverityPredictionAgent
        ↓
ResourceAllocationAgent
        ↓
SimulationAgent
        ↓
StakeholderCommsAgent
        ↓
    END (Pipeline complete)
```

The ChatAgent runs completely independently — it is NOT part of the crisis pipeline. It is triggered only by the frontend chat interface.

### LangGraph Reflection Loop

When the CrisisClassificationAgent produces low confidence or detects unresolved contradictions, the LangGraph topology routes through a Verification → Re-Classification reflection cycle (up to 2 iterations) before proceeding to severity prediction. This is implemented as conditional edges in the StateGraph.

## Master Trace Format

One master trace is logged per crisis event. This acts as the source of truth for the entire pipeline's decision-making process:

```json
{
  "event_id": "uuid",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "total_latency_ms": 4200,
  "agents_executed": [
    "SignalIngestionAgent",
    "CrisisClassificationAgent",
    "SeverityPredictionAgent",
    "ResourceAllocationAgent",
    "SimulationAgent",
    "StakeholderCommsAgent"
  ],
  "final_crisis_id": "uuid",
  "pipeline_status": "completed | retracted | degraded",
  "agent_trace_ids": ["trace-001", "trace-002", "..."]
}
```

## Trace Export

**Endpoint:** `GET /api/traces/export`

Generates a single JSON file containing all agent reasoning traces from all pipeline runs. Each trace includes: input data, reasoning steps (human-readable), confidence scores, decisions made, alternatives considered, and whether a fallback was triggered.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pipeline/run` | Full crisis pipeline (direct orchestrator) |
| `POST` | `/api/pipeline/run/v2` | Full crisis pipeline (LangGraph StateGraph) |
| `POST` | `/api/signals/ingest` | Signal ingestion only |
| `POST` | `/api/classify` | Crisis classification only |
| `POST` | `/api/predict/severity` | Severity prediction only |
| `POST` | `/api/allocate` | Resource allocation only |
| `POST` | `/api/simulate` | Simulation only |
| `POST` | `/api/notify` | Stakeholder communications only |
| `POST` | `/api/verify` | Verification only |
| `POST` | `/api/chat` | Multilingual citizen chat |
| `GET` | `/api/crises/active` | List active crises |
| `GET` | `/api/resources` | Current resource inventory |
| `GET` | `/api/traces/export` | Export all agent traces |
| `POST` | `/demo/scenario-a` | Scenario A (G-10 Flooding) |
| `POST` | `/demo/scenario-b` | Scenario B (False Alarm) |
| `POST` | `/demo/scenario-c` | Scenario C (Dual Crisis) |
| `GET` | `/health` | Cloud Run health check |
