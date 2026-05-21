# Amaan CIRO — Backend

FastAPI + LangGraph multi-agent orchestration engine for the Amaan CIRO crisis response system.

## Architecture

The backend operates as a stateful, cyclic multi-agent workflow powered by LangGraph. A compiled StateGraph coordinates 8 specialized agents, each reporting data and reasoning traces into a central `CrisisState`.

### LangGraph Topology

```
START ──> Ingestion Node ─────────> (Signals Exist?)
                │                         │
          [No Signals]              [Has Signals]
                ▼                         ▼
          END (Idle)            Classification Node
                                          │
                                          ▼
                              (Confidence ≥ 0.50?)
                                 /        │        \
                [Yes]           /         │         \  [No / Contradiction]
                               /          │          \
                              ▼           │           ▼
              Severity Node               │      Verification Node
                      │                   │              │
                      ▼                   ▼              ▼
              Allocation Node       END (Monitor)  (Resolve Contradiction)
                      │                                  │
                      ▼                          Retracted ──> END
              Simulation Node                   Confirmed ──> Severity Node
                      │                          Unclear ──> Reflection Loop (×2) ──> Classification
                      ▼
                 Comms Node
                      │
                      ▼
                     END
```

- **Reflection Loop:** When conflicting signals are ingested, the VerificationAgent performs conflict resolution. If the classification needs adjustment, it feeds correction vectors back to the ClassificationAgent (up to 2 iterations).
- **Trace Logging:** Every node writes reasoning traces (steps, confidence scores, trade-offs, fallback flags) to Firestore under `agent_traces`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pipeline/run` | Full crisis pipeline (direct orchestrator) |
| `POST` | `/api/pipeline/run/v2` | Full pipeline via LangGraph StateGraph |
| `POST` | `/api/chat` | Multilingual citizen chat (English, Urdu, Roman Urdu) |
| `GET` | `/api/crises/active` | List active crisis events |
| `GET` | `/api/resources` | Current fleet inventory |
| `GET` | `/api/traces/export` | Export all agent traces as JSON |
| `GET` | `/health` | Cloud Run health check |

## Setup

### Prerequisites
- Python 3.11+
- Groq API key and/or Gemini API key
- Google Cloud Firestore service account (optional, for trace persistence)

### Installation

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Configuration

Create `.env` in this directory:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
DEMO_MODE=True
```

Setting `DEMO_MODE=True` uses local mock data from `data/demo_scenarios.json` when live APIs are unavailable.

### Running

```bash
uvicorn main:app --reload --port 8000
```

Interactive API docs at [localhost:8000/docs](http://localhost:8000/docs).

## Deployment

The backend is containerized and deployed on Google Cloud Run (serverless, auto-scaling):

```bash
gcloud run deploy amaan-ciro --source . --region asia-south1 --allow-unauthenticated
```

Production API: [amaan-ciro-485623882730.asia-south1.run.app/docs](https://amaan-ciro-485623882730.asia-south1.run.app/docs)
