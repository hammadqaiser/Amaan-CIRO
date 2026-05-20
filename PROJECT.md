# Amaan — Project Vision & Scope

### Production Deployments
*   🌐 **Live Web Command Dashboard (Vercel):** [https://amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app)
*   🧠 **Serverless Agent Engine (Google Cloud Run API & Swagger):** [https://amaan-ciro-485623882730.asia-south1.run.app/docs](https://amaan-ciro-485623882730.asia-south1.run.app/docs)

## One-Line Description
Pakistan's first AI-powered crisis intelligence system that detects, 
detects, classifies, and coordinates emergency response in real time using 
a LangGraph-based multi-agent orchestration StateGraph (built in Antigravity IDE) 
and Vite React high-performance single page web application packaged natively via 
Ionic Capacitor for Android.

## Problem Statement
Pakistan loses billions of rupees annually to preventable crisis 
mismanagement. The 2022 Karachi floods killed 36 people and caused 
PKR 14 billion in damage — not because the crisis was unforeseeable, 
but because response was reactive, fragmented, and slow. Emergency 
services received information from 12 different channels with no 
unified intelligence to tell them where to go first, which signals 
to trust, and how to split limited resources between simultaneous 
emergencies.

Amaan solves this. Not by predicting disasters — by making every 
response decision in seconds, with full transparency on why each 
decision was made.

## Target Users
1. **Emergency Operations Center operators** — primary user, 
   command center view via React web dashboard and Capacitor Android app
2. **NDMA / PDMA field coordinators** — resource allocation 
   and incident tracking
3. **Citizens** — reporting incidents, receiving location-based 
   alerts via React web dashboard and Capacitor Android app
4. **Emergency services (Rescue 1122, Police, Ambulance)** — 
   dispatch coordination and routing

## Success Metrics
- Signal fusion latency: < 5 seconds from signal receipt to classification
- Resource allocation decision: < 10 seconds for single crisis
- False positive rate: < 15% (shown via contradiction detection)
- Simultaneous crises supported: minimum 2 (demo shows 3)
- Capacitor native shell and WebGL map rendering crash rate: 0% during demo
- Antigravity trace completeness: 100% of agent decisions logged

## What We Are NOT Building
- Real 911/Rescue 1122 integration (simulation only)
- Payment systems
- Social media platform
- Web Dashboard for Municipal Emergency Operations Centers
- Web Dashboard for NDMA field coordinators
- Web Dashboard for Hospital administrators
- Web Dashboard for General Public

## Competitive Differentiator
Most crisis systems are dashboards that show what happened.
Amaan is an intelligence system that decides what to do next,
explains every decision, and learns from false alarms.

The Antigravity multi-agent architecture makes every reasoning 
step visible — this is not a black-box AI. Judges, administrators,
and citizens can see exactly why Amaan made each decision.


## Technical Architecture
Amaan uses a hybrid agentic architecture where Google Antigravity 
acts as the central nervous system for crisis intelligence, while 
maintaining full autonomy from the Antigravity platform at runtime.

**1. Agent Architecture (8 Core Agents)**

The system operates as a multi-agent workflow where each agent has 
single responsibility:

- **SignalIngestionAgent** - Ingests 3+ signal sources with real-time 
  normalization
- **CrisisClassificationAgent** - Crisis classification with confidence scoring 
  using multi-stage LLM decision trees
- **SeverityPredictionAgent** - Predicts severity, evolution, duration, affected population
- **ResourceAllocationAgent** - Constrained optimization (vehicles, medical units, 
  evacuation centers) with dynamic re-allocation
- **SimulationAgent** - Before/after state modeling for impact 
  assessment
- **StakeholderCommsAgent** - Generates messages for different audiences (NDMA, Emergency Services, Hospitals, Public, Media) with message personalization
- **VerificationAgent** - False alarm handling and response adjustment
- **ChatAgent** - Multilingual (English, Urdu, Roman Urdu) Q&A 
  about nearby dangers

**2. Technology Stack**
- **Backend:** FastAPI + Google Cloud Run (auto-scaling, serverless)
- **Frontend SPA:** Vite React, TypeScript, and Tailwind CSS (responsive desktop/mobile layout)
- **Mobile Wrapper:** Ionic Capacitor for direct native Android packaging
- **Maps:** MapLibre GL JS (WebGL-accelerated hardware rendering) for real-time crisis and telemetry overlays
- **Database / Logs:** Google Cloud Firestore (real-time storage, agent traces, event logs)
- **Real-time Layer:** Directly integrated Firestore live state synchronization
- **Notifications:** Web-comms and in-console broadcast notifications

**2.1. Backend & Cloud Architecture**

The backend is built with FastAPI and deployed on Google Cloud Run as a
serverless container, ensuring auto-scaling and 24/7 availability. All agent logic runs within the backend process, maintaining complete runtime autonomy from the Antigravity development environment. Key infrastructure components include:

**2.2. Mapping & Geospatial Intelligence**

- **MapLibre GL WebGL Engine** - Hardware-accelerated vector mapping with rich styling and neon dark-mode UI
- **Real-time Interactive Incidents Layer** - Dynamically renders interactive coordinates for flooding, heatwave, traffic congestion, and medical dispatch assets
- **Geohash-based Location Clustering** - Automatic aggregation of citizen reports within 500m radius for efficient dispatch
- **Real-time Traffic Routing** - Dynamic re-routing routes around active flood zones and accidents
- **Custom Crisis Overlay** - Heatmap visualization of crisis density, affected areas, and emergency response coverage

**2.3. Mobile Packaging & Android Shell (Ionic Capacitor)**

The high-fidelity Vite React web application is seamlessly packaged into a native Android APK using **Ionic Capacitor**. This enables 60FPS WebGL map rendering and smooth animations without native platform performance degradation. Key features include:

- **Universal Core SPA** - Identical high-performance TypeScript code runs in both mobile APK and desktop browsers, maximizing consistency
- **Real-time Crisis Command Bridge** - Live map canvas with interactive overlays, satellite broadcast news panel, and tactical fleet inventory
- **Citizen Reporting Panel** - Interactive form for reporting incidents with live geocoding and severity assessment
- **Multilingual Chat Console** - Embedded translation-aware ChatAgent facilitating Q&A in English, Urdu, and Roman Urdu
- **System Diagnostics and Telemetry** - Real-time metrics on response latency, allocated resources, and agent trace reasoning

**2.4. Multi-Agent Orchestration (Runtime)**

All agents are implemented as independent Python classes within the FastAPI backend. LangGraph is used as the orchestration engine to manage state, routing, and loops. Key orchestration patterns include:

- **LangGraph StateGraph Orchestration** - Manages state transitions, conditional edges, and reflection loops.
- **Sequential Agent Chaining** - Nodes run sequentially: Ingestion → Classification → Severity → Allocation → Simulation → Comms.
- **Conditional Routing** - The graph routes to the VerificationAgent if low-confidence alerts or contradictions are detected.
- **Self-Correction Reflection Loop** - If the VerificationAgent identifies logical discrepancies, it feeds instructions back into the Classification node (max 2 iterations) to re-evaluate raw signals under a corrected premise.
- **Reasoning-Trace Logging** - Every agent decision logs reasoning steps, confidence score, decision made, alternative considered, and fallback status, writing directly to Cloud Firestore.

Antigravity was used as the development environment for:
- Writing and testing all agent code
- Generating Antigravity trace logs during development
- Spec-driven implementation planning

**2.5. LLM Inference & Fallback Strategy**

The system uses a multi-LLM inference strategy to ensure 24/7 
availability and cost optimization:

- **Primary Model:** Google Gemini 2.0 Flash 
- **Fallback Strategy (optional):**
  1. Groq API (high-speed, cost-effective)
  2. Gemini API (direct access, rate-limit aware)
  3. OpenRouter API (multi-model support)


**2.6. Database & Real-time Infrastructure**
The system uses a dual-database architecture for optimal performance and scalability:

- **Google Cloud Firestore** - Primary database for real-time synchronization, incident updates, and agent trace tracking.
- **Firestore Live Subscriptions** - High-speed, low-latency live synchronization of active crises, chat logs, and fleet units.
- **In-Console Notifications** - Client-side live alert system with sound cues and visual toasts for EOC operators.

This architecture ensures that emergency data is always available in real-time, while also providing the scalability needed for large-scale crisis management.

**2.7. Integration with Existing Systems**

While Amaan operates autonomously, it seamlessly integrates with Pakistan's extisting emergency management infrastructure:

- **Rescue 1122** - Standard emergency response coordination protocol adopted for all dispatch operations
- **NDMA (National Disaster Management Authority)** - Utilizes NDMA's historical vulnerability data and response guidelines
- **PMD (Pakistan Meteorological Department)** - Direct API integration for weather and climate data (Open-Meteo as primary, OpenWeatherMap as fallback)
- **Google Maps Platform** - Integration with Google Maps services for traffic routes, geocoding, and distance calculations

**3. Data Flow (Runtime Autonomy)**
At runtime, the system is fully independent of Google Antigravity:
- Backend runs as a standalone Docker container on Cloud Run
- Antigravity SDK orchestrates agents within the backend process
- All decision traces and logs are exported to JSON for hackathon 
  submission

**4. Crisis Intelligence Workflow**
1. SignalIngestionAgent combines weather, traffic, social signals with weighted confidence scoring
2. CrisisClassificationAgent assigns crisis type (urban flood, heatwave, accident) with sub-type classification (e.g., infrastructure failure)
3. SeverityPredictionAgent predicts severity, evolution, duration, affected population
4. ResourceAllocationAgent allocates emergency resources using constrained optimization algorithm (vehicle dispatch, evacuation routing)
5. SimulationAgent models before/after states for impact assessment
6. StakeholderCommsAgent generates messages for different audiences
7. VerificationAgent handles false positives via cross-validation
8. ChatAgent provides multilingual Q&A via Capacitor app. It can be accessed independently of the pipeline above. This is for citizens to query about nearby dangers.

**5. Deployment Model**
The architecture is designed for 24/7 operation: 
- Serverless scaling with Google Cloud Run
- Automatic failover between LLM providers
- Local mock data layer for demo reliability
- Offline support for 4+ hours in Capacitor wrapper

**6. Key Architectural Innovations**
- **Multi-Agent Autonomy:** Full runtime independence from development environment
- **Explainable AI:** Every decision has documented reasoning trace
- **Fail-Safe Design:** LLM provider fallback ensures 100% uptime
- **Crisis-Aware Routing:** Not a linear pipeline, but a dynamic workflow based on crisis type
- **Scalability:** Handles multiple simultaneous crises with auto-scaling
- **Cost Optimization:** Automatic provider selection minimizes operational cost