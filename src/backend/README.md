# Amaan CIRO - FastAPI & LangGraph Agentic Orchestrator

This directory houses the backend server for the **Amaan (CIRO) - Crisis Intelligence & Response Orchestrator** system. It is implemented in high-performance asynchronous Python utilizing FastAPI and LangGraph.

---

## 🧠 Architectural Overview

Amaan's crisis brain operates as a stateful, cyclic multi-agent workflow powered by **LangGraph**. The orchestrator compiles a dynamic StateGraph where each emergency decision is executed by specialized agents reporting their raw data and reasoning tracks back into a central `CrisisState`.

### LangGraph Topology

```
START ──> Ingestion Node ─────────> (Check If Signals Exist?)
                │                               │
                │ [No Signals]                  │ [Has Signals]
                ▼                               ▼
               END (Idle)               Classification Node
                                                │
                                                ▼
                                    (Evaluate Confidence / Conflicts)
                                       /        │        \
             [Confidence >= 0.50]     /         │         \ [Confidence < 0.50 / Contradiction]
                                     /          │          \
                                    ▼           │           ▼
                    Severity Node               │      Verification Node
                            │                   │              │
                            ▼                   ▼              ▼
                    Allocation Node        END (Monitoring) (Perform Contradiction Resolution)
                            │                                  │
                            ▼                                  ├─> Retracted Alert ──> END
                    Simulation Node                            │
                            │                                  ├─> Confirmed Alert ──> Severity Node
                            ▼                                  │
                       Comms Node                              └─> Reflection Loop (Max 2) ──> Classification
                            │
                            ▼
                           END (Comms Dispatched)
```

*   **Self-Correction Reflection Loop:** When conflicting signals are ingested (e.g. water main burst vs. urban rainfall), the `VerificationAgent` performs real-time conflict-resolution. If it determines a core classification premise needs adjustment, it feeds detailed correction vectors back into the `CrisisClassificationAgent` node (looping up to 2 times) to re-evaluate the crisis under a refined context.
*   **Firestore Telemetry Integration:** Every single node in the LangGraph execution path writes detailed traces (reasoning steps, confidence scores, trade-offs analyzed, fallback flags, and final choices) into Firestore under the `agent_traces` collection.

---

## 🛠️ FastAPI Endpoint Specifications

*   `POST /api/pipeline/run`: Ingests a new set of location metrics, compiles the LangGraph StateGraph, executes the multi-agent pipeline, and returns the unified incident orchestration plan.
*   `POST /api/chat`: Standalone conversational endpoint routed to the **ChatAgent** providing bilingual (English, Urdu, Roman Urdu) safety advice with localized geohash spatial queries.
*   `GET /api/traces/export`: Gathers all logged execution traces and compiles the standard JSON file for hackathon jury submission.
*   `GET /api/crises/active`: Fetches the live list of currently tracked, active crisis events from Cloud Firestore.
*   `GET /api/resources`: Retrieves current tactical fleet inventories (ambulances, boats, rescue teams).
*   `GET /health`: Health-check endpoint for Google Cloud Run container verification.

---

## 💻 Local Setup & Execution

### Prerequisites
*   Python 3.11+
*   Google Firebase / Cloud Firestore Service Account Key (set as `GOOGLE_APPLICATION_CREDENTIALS`)
*   Groq API Key (set as `GROQ_API_KEY`) and/or Gemini API Key (set as `GEMINI_API_KEY`)

### 1. Installation
Create and activate a clean Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate      # Windows Powershell
source venv/bin/activate   # macOS / Linux
```
Install backend dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Configurations
Configure the local environment variables in a `.env` file at `src/backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
FIRESTORE_PROJECT_ID=your_gcp_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase/service-account.json
DEMO_MODE=True
```
*Note: If `DEMO_MODE` is set to `True`, the backend will dynamically fallback to local mock data (from `data/demo_scenarios.json` and `data/ict_vulnerability.json`) if Google Cloud Run Firestore/LLM endpoints are offline.*

### 3. Running the Server
Launch the FastAPI uvicorn daemon:
```bash
uvicorn main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive OpenAPI/Swagger Documentation interface.

---

## 🚀 Google Cloud Run Production Deployment

Amaan's backend is fully containerized and hosted on serverless **Google Cloud Run**, delivering high-availability and automatic scaling down to zero.

### Deploying the container:
```bash
gcloud run deploy amaan-ciro --source . --region asia-south1 --allow-unauthenticated
```
