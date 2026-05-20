# CIRO Data Flows & Orchestration

This document outlines the system data flow, orchestrator sequence, and API endpoints for the Amaan (CIRO) system.

## ORCHESTRATOR

The orchestrator chains all agents in the correct sequence.
It is NOT a framework — it is a plain Python class with explicit logic.
It runs entirely within the FastAPI backend process.

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
StakeholderCommsAgent (async — does not block)
        ↓
VerificationAgent (monitoring loop — runs every 30 min independently)
```
 
ChatAgent runs completely independently.
It is NOT part of the crisis pipeline.
It is triggered only by the React/Capacitor app Chat tab console.

### Orchestrator Master Trace
 
One master trace is logged per crisis event to Firestore. This acts as the source of truth for the entire pipeline's decision-making process:
 
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
    "StakeholderCommsAgent",
    "VerificationAgent"
  ],
  "final_crisis_id": "uuid",
  "pipeline_status": "completed | retracted | degraded",
  "agent_trace_ids": ["trace-001", "trace-002", "trace-003"]
}
```

## AGENT TRACE EXPORT
 
**FastAPI Endpoint:** `GET /api/traces/export`
 
This endpoint generates the single JSON file to attach to the
hackathon submission as proof of Antigravity agent traces.
 
### Export Format
 
```json
{
  "export_timestamp": "2026-05-20T12:00:00Z",
  "system": "Amaan Crisis Intelligence — CIRO Challenge",
  "hackathon": "Google AI Seekho 2026 — Antigravity Hackathon",
  "built_with": "Google Antigravity IDE",
  "runtime_platform": "FastAPI on Google Cloud Run — no Antigravity dependency",
  "total_traces": 47,
  "pipeline_runs": [
    {
      "event_id": "uuid",
      "scenario": "Scenario A — G-10 Islamabad Flooding",
      "pipeline_status": "completed",
      "total_latency_ms": 4200,
      "traces": [
        {
          "agent": "SignalIngestionAgent",
          "trace_id": "trace-001",
          "confidence_score": 0.87,
          "fallback_triggered": false,
          "reasoning_steps": ["..."]
        },
        {
          "agent": "CrisisClassificationAgent",
          "trace_id": "trace-002"
        },
        {
          "agent": "SeverityPredictionAgent",
          "trace_id": "trace-003"
        },
        {
          "agent": "ResourceAllocationAgent",
          "trace_id": "trace-004"
        },
        {
          "agent": "SimulationAgent",
          "trace_id": "trace-005"
        },
        {
          "agent": "StakeholderCommsAgent",
          "trace_id": "trace-006"
        },
        {
          "agent": "VerificationAgent",
          "trace_id": "trace-007"
        }
      ]
    },
    {
      "event_id": "uuid-2",
      "scenario": "Scenario B — False Alarm Recovery"
    },
    {
      "event_id": "uuid-3",
      "scenario": "Scenario C — Dual Crisis G-10 + I-8"
    }
  ]
}
```

## QUICK REFERENCE — API ENDPOINTS
 
```
POST /api/pipeline/run          ← trigger full crisis pipeline
POST /api/signals/ingest        ← SignalIngestionAgent
POST /api/classify              ← CrisisClassificationAgent
POST /api/predict/severity      ← SeverityPredictionAgent
POST /api/allocate              ← ResourceAllocationAgent
POST /api/simulate              ← SimulationAgent
POST /api/notify                ← StakeholderCommsAgent
POST /api/verify                ← VerificationAgent
POST /api/chat                  ← ChatAgent (Phase 2)
GET  /api/crises/active         ← Frontend app retrieves active list
GET  /api/resources             ← Frontend resource screen
GET  /api/traces/export         ← Hackathon submission trace file
GET  /health                    ← Cloud Run health check
```
