# AGENTS.md — Amaan Crisis Intelligence System
## Agent Definitions, Contracts & Orchestration Logic

---

## CRITICAL RULE

All agents are independent Python classes in the FastAPI backend.
They call Gemini 2.0 Flash directly via google-generativeai SDK.
No agent has any runtime dependency on Antigravity.
Antigravity was used as the IDE to build and test them — nothing more.

Every agent MUST:
1. Accept a typed Pydantic input model
2. Return a typed Pydantic output model
3. Call self.log_trace() before returning any result
4. Handle API failure with a defined fallback
5. Never raise unhandled exceptions — catch and return degraded output

---

## BASE AGENT CONTRACT

**File:** `backend/agents/base_agent.py`

All 8 agents inherit from this base class.
Provides Gemini client, Firestore logging, and trace generation.
Never duplicate these methods in individual agents.

```python
import google.generativeai as genai
from firebase_admin import firestore
from datetime import datetime, timezone
from typing import Any
import json
import uuid

class BaseAgent:
    """
    Base class for all Amaan agents.
    Provides Gemini client, Firestore logging, and trace generation.
    Every agent inherits this — never duplicate these methods.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        self.db = firestore.client()

    def call_gemini(self, prompt: str, fallback: dict) -> tuple[dict, bool]:
        """
        Call Gemini 2.0 Flash. Returns parsed JSON dict + fallback_triggered boolean.
        On any failure, returns fallback dict and sets fallback_triggered=True.
        """
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text), False
        except Exception as e:
            print(f"[{self.agent_name}] Gemini failed: {e}. Using fallback.")
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
        Judges read these — keep reasoning_steps human-readable.
        Returns the trace dict for inclusion in agent output.
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
        self.db.collection("agent_traces").document(trace_id).set(trace)
        return trace
```

---

## ORCHESTRATOR & DATA FLOWS

See [DATA_FLOWS.md](DATA_FLOWS.md) for the complete execution order, orchestrator master trace format, and API endpoints.

---

## AGENT 1 — SignalIngestionAgent
 
**File:** `backend/agents/signal_ingestion.py`
**Build order:** First — all other agents depend on its output
**Evaluation relevance:** Crisis Detection 25%, Robustness 10%
 
### Single Responsibility
 
Fetch raw signals from all configured data sources.
Normalize them into the standard RawSignal schema.
Score each signal for source credibility.
Flag signals that are temporally stale (older than 2 hours).

### Antigravity Trace Must Include
- Each signal received with raw credibility
- Staleness adjustment applied
- Contradiction detected (yes/no, which signals)
- Final fused confidence score with reasoning

### Input Model
 
```python
class SignalIngestionInput(BaseModel):
    location: dict          # {"lat": 33.72, "lng": 73.04, "city": "Islamabad"}
    radius_km: float        # search radius — default 10.0
    time_window_hours: int  # lookback window — default 2
```
 
### Output Model
 
```python
class RawSignal(BaseModel):
    signal_id: str
    source: str             # "pmd" | "google_traffic" | "gdelt" |
                            # "citizen_app" | "mock"
    signal_type: str        # "weather" | "traffic" | "social" | "field_report"
    content: str            # plain text description of the signal
    location: dict          # {"lat", "lng", "address"}
    timestamp: str          # ISO 8601 format
    credibility_score: float  # 0.0 to 1.0 — see scoring table below
    staleness_flag: bool    # True if signal is older than 2 hours
    raw_data: dict          # original API response preserved
 
class SignalIngestionOutput(BaseModel):
    signals: list[RawSignal]
    total_signals: int
    sources_contacted: list[str]
    sources_failed: list[str]
    fallback_used: bool
    trace: dict
```
 
### Credibility Scoring Table
 
| Source | Score Range |
|--------|------------|
| Pakistan Met Dept (PMD) official | 0.90 – 0.95 |
| Google Maps Traffic API | 0.85 – 0.90 |
| GDELT verified news source | 0.65 – 0.75 |
| GDELT social media signal | 0.40 – 0.60 |
| Citizen app field report | 0.70 |
| Mock/pre-scripted demo signal | 0.80 |
| Anonymous unverified report | 0.20 – 0.35 |
 
### Staleness Rule
 
Any signal with timestamp older than 2 hours before current time:
- Set `staleness_flag = True`
- Reduce `credibility_score` by 0.30 (floor at 0.10)
- Include in output but mark clearly for ClassificationAgent to handle
### Primary API — Open-Meteo (Free, No Key Required)
 
```python
async def _fetch_weather(self, location: dict) -> list[RawSignal]:
    """
    Fetch rainfall and temperature from Open-Meteo.
    Free tier, no API key, 10,000 calls/day.
    Use as primary weather source — PMD does not have a public REST API.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={location['lat']}&longitude={location['lng']}"
        f"&hourly=precipitation,temperature_2m,windspeed_10m"
        f"&current_weather=true"
        f"&timezone=Asia/Karachi"
    )
    # On failure: return mock signal from data/demo_scenarios.json
```
 
### Secondary API — GDELT (Free, No Key Required)
 
```python
async def _fetch_social_signals(self, location: dict) -> list[RawSignal]:
    """
    Fetch crisis-related news and social signals from GDELT Project.
    Completely free, real-time, covers Pakistan extensively.
    """
    url = (
        f"https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query=flood+islamabad+pakistan"
        f"&mode=artlist&maxrecords=10&format=json&timespan=24h"
    )
    # On failure: return mock signals from data/demo_scenarios.json
```
 
### Fallback Behavior
 
When ALL live APIs fail simultaneously:
1. Load pre-scripted signals from `data/demo_scenarios.json` matching requested location
2. Set `fallback_used = True`
3. Log all failed sources in `sources_failed` list
4. Pipeline continues — API failure never blocks the system
### Example Trace Reasoning Steps
 
```json
[
  "Contacted 4 sources: Open-Meteo, Google Traffic, GDELT, Citizen App",
  "Open-Meteo returned: 82mm rainfall in 3 hours at G-10 — credibility 0.92",
  "Google Traffic returned: severe congestion on Jinnah Ave — credibility 0.87",
  "GDELT returned: 3 social posts about flooding in G-10 — avg credibility 0.58",
  "Citizen app returned: 1 field report claiming water main burst — credibility 0.70",
  "Field report timestamp is 4 hours old — staleness_flag set, credibility reduced to 0.40",
  "Twitter API failed (rate limit) — fallback mock signal loaded",
  "Total: 6 signals collected, 1 stale-flagged, 1 from fallback"
]
```

---
## AGENT 2 — CrisisClassificationAgent
 
**File:** `backend/agents/crisis_classification.py`
**Build order:** Second
**Evaluation relevance:** Crisis Detection 25% (highest weighted criterion)
 
### Single Responsibility
 
Receive normalized signals from SignalIngestionAgent.
Classify the dominant crisis type with a confidence score.
Detect contradictions between conflicting signals.
Output a CrisisObject that all downstream agents use

### Antigravity Trace Must Include
- Classification decision with probability distribution
- All rules triggered and their weights
- Severity justification with data points
- Duration estimate methodology


### Input Model
 
```python
class CrisisClassificationInput(BaseModel):
    signals: list[RawSignal]        # from SignalIngestionAgent
    location: dict
    historical_context: dict        # NDMA vulnerability data for this location
```
 
### Output Model
 
```python
class CrisisObject(BaseModel):
    crisis_id: str
    crisis_type: str            # "urban_flood" | "heatwave" | "accident" |
                                # "power_outage" | "infrastructure" | "compound"
    sub_type: str               # "flash_flood" | "basement_flood" | "road_flood"
    location: dict
    confidence_score: float     # 0.0 to 1.0
    contradictions_detected: bool
    contradiction_detail: str | None
    dominant_signals: list[str]     # signal_ids supporting this classification
    dismissed_signals: list[str]    # signal_ids dismissed with reasons
    status: str                 # "active" | "unverified" | "retracted"
    trace: dict
 
class CrisisClassificationOutput(BaseModel):
    primary_crisis: CrisisObject
    secondary_crisis: CrisisObject | None   # populated for simultaneous crises
    classification_method: str              # "gemini_inference" | "rule_based_fallback"
    trace: dict
```
 
### Gemini Prompt Template
 
```python
CLASSIFICATION_PROMPT = """
You are a crisis classification AI for Pakistan Emergency Management.
 
Analyze these signals and classify the crisis:
{signals_json}
 
Historical vulnerability data for this area:
{historical_context}
 
Current season: {season}
Current time: {current_time}
 
Classification rules to apply:
- Monsoon season (July–September) + rainfall >50mm/3hrs = boost urban_flood probability by +0.25
- G-10, I-10, G-11, G-13 Islamabad = high flood vulnerability sectors
- Temperature >42°C + low-income sector = classify as heatwave emergency
- PMD official alert + any corroborating signal = minimum confidence 0.75
 
Contradiction resolution rules:
- Two signals conflict → check timestamps, prefer newer signal
- Credibility difference >0.30 → prefer higher credibility source
- Contradiction cannot be resolved → set confidence <0.50, status=unverified
 
Return ONLY this JSON — no other text, no markdown:
{{
  "crisis_type": "string",
  "sub_type": "string",
  "confidence_score": 0.0,
  "contradictions_detected": false,
  "contradiction_detail": "string or null",
  "dominant_signal_ids": [],
  "dismissed_signal_ids": [],
  "dismissal_reasons": [],
  "reasoning": "2-3 sentences plain English explanation of why this classification was made"
}}
"""
```
 
### Rule-Based Fallback (When Gemini Unavailable)
 
```python
def _rule_based_classify(self, signals: list) -> dict:
    """
    Deterministic fallback. Uses signal keywords and credibility scores only.
    Applied when Gemini API is unavailable during demo or rate-limited.
    """
    flood_signals = [
        s for s in signals
        if any(kw in s.content.lower() for kw in ["rain", "flood", "water", "submerged"])
        and not s.staleness_flag
    ]
    heat_signals = [
        s for s in signals
        if any(kw in s.content.lower() for kw in ["heat", "temperature", "heatwave"])
        and not s.staleness_flag
    ]
 
    if len(flood_signals) >= 2:
        avg_cred = sum(s.credibility_score for s in flood_signals) / len(flood_signals)
        return {
            "crisis_type": "urban_flood",
            "sub_type": "flash_flood",
            "confidence_score": min(0.65, avg_cred),
            "contradictions_detected": False,
            "contradiction_detail": None,
            "reasoning": "Rule-based fallback: multiple flood signals detected"
        }
    elif len(heat_signals) >= 2:
        return {
            "crisis_type": "heatwave",
            "sub_type": "extreme_heat",
            "confidence_score": 0.60,
            "contradictions_detected": False,
            "contradiction_detail": None,
            "reasoning": "Rule-based fallback: multiple heat signals detected"
        }
    else:
        return {
            "crisis_type": "unknown",
            "sub_type": "unclassified",
            "confidence_score": 0.30,
            "contradictions_detected": False,
            "contradiction_detail": None,
            "reasoning": "Rule-based fallback: insufficient signals for classification"
        }
```
 
### Contradiction Detection Logic (Scenario A)

See [SCENARIOS.md](SCENARIOS.md) for the step-by-step contradiction logic expected in Scenario A.

---
## AGENT 3 — SeverityPredictionAgent
 
**File:** `backend/agents/severity_prediction.py`
**Build order:** Third
**Evaluation relevance:** Crisis Detection 25%
 
### Single Responsibility
 
Predict severity level, geographic spread, affected population,
expected duration, and evolution timeline of the classified crisis.
This agent produces the quantitative impact numbers shown in the demo.

### Antigravity Trace Must Include:
- Classification decision with probability distribution
- All rules triggered and their weights
- Severity justification with data points
- Duration estimate methodology


### Input Model
 
```python
class SeverityPredictionInput(BaseModel):
    crisis: CrisisObject
    weather_data: dict          # current rainfall rate, wind, temperature
    vulnerability_data: dict    # NDMA sector scores for the affected location
    historical_events: list     # similar past events from NDMA static database
```
 
### Output Model
 
```python
class SeverityPrediction(BaseModel):
    severity_level: int             # 1 (minor) to 5 (catastrophic)
    severity_label: str             # "Minor" | "Moderate" | "Severe" |
                                    # "Critical" | "Catastrophic"
    affected_radius_km: float
    affected_population: int
    estimated_duration_hours: float
    peak_impact_time: str           # ISO timestamp — when crisis will be worst
    spread_risk: float              # 0.0 to 1.0 — probability of expanding
    cascading_risks: list[str]      # e.g. ["power_outage", "road_closure"]
    uncertainty_range: str          # e.g. "±2 hours, ±15% population estimate"
    trace: dict
```
 
### Severity Level Thresholds
 
| Level | Label | Affected Population |
|-------|-------|-------------------|
| 1 | Minor | < 1,000 |
| 2 | Moderate | 1,000 – 10,000 |
| 3 | Severe | 10,000 – 50,000 |
| 4 | Critical | 50,000 – 150,000 |
| 5 | Catastrophic | > 150,000 |
 
### Calculation Formulas
 
```python
# Urban flood duration estimate
duration_hours = (rainfall_mm / drainage_capacity_mm_per_hour) * 1.3
# 1.3 = Islamabad historical drainage performance coefficient from NDMA data
 
# Spread risk (0.0 to 0.95 max)
spread_risk = (rainfall_intensity_mm_per_hr / 10.0) * (1.0 - drainage_capacity_score)
 
# Affected population estimate
area_sqkm = pi * (affected_radius_km ** 2)
affected_population = int(area_sqkm * population_density_per_sqkm * vulnerability_score)
```
 
### ICT Vulnerability Data
 
**File:** `data/ict_vulnerability.json`
 
Pre-populate with this data before starting any agent implementation:
 
```json
{
  "G-10": {
    "flood_vulnerability": 0.85,
    "drainage_capacity_mm_per_hr": 12,
    "population_density_per_sqkm": 8500,
    "low_income_flag": false,
    "historical_flood_events": 7,
    "area_sqkm": 4.2
  },
  "G-11": {
    "flood_vulnerability": 0.80,
    "drainage_capacity_mm_per_hr": 13,
    "population_density_per_sqkm": 7800,
    "low_income_flag": false,
    "historical_flood_events": 5,
    "area_sqkm": 4.5
  },
  "G-13": {
    "flood_vulnerability": 0.78,
    "drainage_capacity_mm_per_hr": 14,
    "population_density_per_sqkm": 7100,
    "low_income_flag": false,
    "historical_flood_events": 5,
    "area_sqkm": 5.0
  },
  "I-8": {
    "flood_vulnerability": 0.60,
    "drainage_capacity_mm_per_hr": 18,
    "population_density_per_sqkm": 6200,
    "low_income_flag": true,
    "historical_flood_events": 3,
    "area_sqkm": 3.8
  },
  "I-10": {
    "flood_vulnerability": 0.72,
    "drainage_capacity_mm_per_hr": 15,
    "population_density_per_sqkm": 9100,
    "low_income_flag": true,
    "historical_flood_events": 6,
    "area_sqkm": 4.1
  },
  "F-6": {
    "flood_vulnerability": 0.30,
    "drainage_capacity_mm_per_hr": 28,
    "population_density_per_sqkm": 3200,
    "low_income_flag": false,
    "historical_flood_events": 1,
    "area_sqkm": 6.0
  },
  "F-7": {
    "flood_vulnerability": 0.25,
    "drainage_capacity_mm_per_hr": 30,
    "population_density_per_sqkm": 2800,
    "low_income_flag": false,
    "historical_flood_events": 0,
    "area_sqkm": 5.5
  }
}
```
---

## AGENT 4 — ResourceAllocationAgent
 
**File:** `backend/agents/resource_allocation.py`
**Build order:** Fourth — spend the MOST time here
**Evaluation relevance:** Resource Optimization 20% (second highest criterion)
 
### Single Responsibility
 
Optimize allocation of constrained emergency resources across
one or more simultaneous crises. Every single allocation decision
must have a written justification that a human can read and verify.
Show explicit trade-offs when two crises compete for the same resource.

### Antigravity Trace Must Include
- Impact score calculation for each crisis
- Resource requirement calculation
- Availability check results
- Travel time for each resource
- Constraint violations detected and how resolved
- Trade-off explanation for shared resources
- Final allocation with written justification

### Input Model
 
```python
class ResourceAllocationInput(BaseModel):
    crises: list[CrisisObject]                   # 1 or 2 simultaneous crises
    severity_predictions: list[SeverityPrediction]
    resource_inventory: ResourceInventory
    constraints: AllocationConstraints
```
 
### Resource Inventory Schema
 
**Firestore collection:** `resource_inventory`
**Local cache:** `data/resource_inventory.json`
 
```python
class ResourceGroup(BaseModel):
    total: int
    available: int
    locations: list[dict]       # [{"lat": float, "lng": float, "unit_id": str}]
 
class ShelterUnit(BaseModel):
    name: str
    capacity: int
    occupied: int
    location: dict              # {"lat", "lng", "address"}
 
class ResourceInventory(BaseModel):
    ambulances: ResourceGroup
    rescue_boats: ResourceGroup
    rescue_teams: ResourceGroup
    police_traffic_units: ResourceGroup
    medical_outreach_teams: ResourceGroup
    water_tankers: ResourceGroup
    generators: ResourceGroup
    shelters: list[ShelterUnit]
 
class AllocationConstraints(BaseModel):
    budget_pkr: float           # maximum operational spend — default 500000
    max_travel_minutes: int     # resource cannot be sent further — default 30
    crew_shift_hours: int       # max hours per crew shift — default 8
```
 
### Starting Resource Inventory
 
**File:** `data/resource_inventory.json`
 
```json
{
  "ambulances": {
    "total": 12, "available": 8,
    "locations": [
      {"lat": 33.7215, "lng": 73.0433, "unit_id": "AMB-01"},
      {"lat": 33.6938, "lng": 73.0651, "unit_id": "AMB-02"},
      {"lat": 33.7394, "lng": 73.0840, "unit_id": "AMB-03"},
      {"lat": 33.6745, "lng": 72.9836, "unit_id": "AMB-04"}
    ]
  },
  "rescue_boats": {
    "total": 6, "available": 4,
    "locations": [
      {"lat": 33.7200, "lng": 73.0500, "unit_id": "BOAT-01"},
      {"lat": 33.6900, "lng": 73.0700, "unit_id": "BOAT-02"}
    ]
  },
  "rescue_teams": {
    "total": 8, "available": 6,
    "locations": [
      {"lat": 33.7100, "lng": 73.0600, "unit_id": "TEAM-01"},
      {"lat": 33.7300, "lng": 73.0400, "unit_id": "TEAM-02"},
      {"lat": 33.6800, "lng": 73.0900, "unit_id": "TEAM-03"}
    ]
  },
  "police_traffic_units": {
    "total": 10, "available": 7,
    "locations": []
  },
  "medical_outreach_teams": {
    "total": 4, "available": 3,
    "locations": []
  },
  "water_tankers": {
    "total": 5, "available": 5,
    "locations": []
  },
  "generators": {
    "total": 8, "available": 6,
    "locations": []
  },
  "shelters": [
    {
      "name": "G-10 Markaz Community Center",
      "capacity": 300, "occupied": 0,
      "location": {"lat": 33.7047, "lng": 73.0079, "address": "G-10 Markaz, Islamabad"}
    },
    {
      "name": "I-8 Government School",
      "capacity": 200, "occupied": 0,
      "location": {"lat": 33.6923, "lng": 73.0612, "address": "I-8/2, Islamabad"}
    },
    {
      "name": "Rawalpindi Sports Complex",
      "capacity": 500, "occupied": 0,
      "location": {"lat": 33.5651, "lng": 73.0169, "address": "Rawalpindi"}
    }
  ]
}
```
 
### Output Model
 
```python
class CrisisAllocation(BaseModel):
    crisis_id: str
    resources_assigned: dict        # {"ambulances": 2, "rescue_teams": 4, ...}
    dispatch_order: list[dict]      # ordered list: unit_id, travel_time_min, priority
    justification: str              # plain English — why this exact allocation
 
class AllocationPlan(BaseModel):
    plan_id: str
    crisis_allocations: list[CrisisAllocation]
    unmet_needs: list[str]          # resources requested but unavailable
    trade_off_explanation: str      # what was sacrificed and why — plain English
    total_resources_deployed: int
    estimated_cost_pkr: float
    fairness_check: str             # confirms low-income areas not deprioritized
    trace: dict
```
 
### Allocation Algorithm — Implement Exactly
 
```python
def allocate(
    self,
    crises: list,
    severity_predictions: list,
    inventory: ResourceInventory,
    constraints: AllocationConstraints
) -> AllocationPlan:
    """
    Multi-crisis resource allocation with fairness guarantee.
 
    Step 1: Calculate impact score for each crisis
      impact_score = severity_level × affected_population × spread_risk
      Fairness bonus: low_income_area == True → impact_score × 1.15
 
    Step 2: Rank crises by impact_score (highest first)
 
    Step 3: For each crisis in ranked order:
      a. Determine resource requirements by crisis type + severity:
 
         urban_flood severity 4:
           rescue_boats: 4, rescue_teams: 4,
           police_traffic_units: 3, ambulances: 2
 
         urban_flood severity 3:
           rescue_boats: 2, rescue_teams: 3,
           police_traffic_units: 2, ambulances: 2
 
         heatwave severity 3:
           medical_outreach_teams: 3, ambulances: 3, water_tankers: 2
 
         heatwave severity 2:
           medical_outreach_teams: 2, ambulances: 2, water_tankers: 1
 
      b. For each required resource type:
           i.   Check available count in inventory
           ii.  Calculate travel_time via Google Maps Distance Matrix API
                (fallback: estimate = distance_km / 40 * 60 minutes)
           iii. Check constraint: travel_time <= max_travel_minutes
           iv.  Check constraint: estimated_cost <= remaining_budget
           v.   If available + within constraints: allocate, decrement inventory
           vi.  If unavailable: add to unmet_needs with explanation
 
      c. Build dispatch_order sorted by travel_time ascending
         (closest available units dispatched first)
 
    Step 4: Generate trade_off_explanation using Gemini
      Pass allocation summary, unmet needs, impact scores.
      Result: 2-3 sentences plain Pakistani English.
 
    Step 5: Fairness check
      Verify no low_income_flag sector received proportionally fewer
      resources than its impact score warrants.
      Generate fairness_check string summarizing the check result.
    """
```
 
### Gemini Prompt — Trade-Off Explanation
 
```python
ALLOCATION_EXPLAIN_PROMPT = """
You are an emergency resource coordinator for Pakistan.
 
Resources allocated to these crises:
{allocation_json}
 
Resources unavailable or not allocated:
{unmet_needs}
 
Impact scores:
{impact_scores}
 
Write a 2-3 sentence plain English explanation of:
1. Why the allocation was made this way
2. What trade-off was made between competing needs
3. What risk remains that was not addressed
 
Write in simple Pakistani English. No technical jargon.
Return ONLY the explanation as a plain string. No JSON wrapper.
"""
```
 
### Scenario C Demo Expected Output

See [SCENARIOS.md](SCENARIOS.md) for the exact multi-crisis resource allocation and trade-off explanation expected for Scenario C.
---

## AGENT 5 — SimulationAgent
 
**File:** `backend/agents/simulation.py`
**Build order:** Fifth
**Evaluation relevance:** Impact Simulation 15%
 
### Single Responsibility
 
Model the before state, the response actions, and the expected
after state for each crisis. Compute measurable improvement metrics.
Always include baseline comparison against manual/non-agentic response.
The before/after visualization in the React/Capacitor app is driven by this agent.

### Antigravity Trace Must Include
- Before state snapshot
- Each action simulated with expected outcome
- After state snapshot
- Amaan vs Baseline comparison table
- Cost/latency estimate

### Input Model
 
```python
class SimulationInput(BaseModel):
    crisis: CrisisObject
    severity: SeverityPrediction
    allocation: AllocationPlan
```
 
### Output Model
 
```python
class CrisisState(BaseModel):
    population_at_risk: int
    roads_blocked: list[str]
    hospital_capacity_used_pct: float
    estimated_casualties_if_unaddressed: int
    response_coverage_pct: float
 
class ResponseAction(BaseModel):
    action_type: str            # "traffic_reroute" | "dispatch_rescue" |
                                # "hospital_prealert" | "public_alert" |
                                # "shelter_open" | "power_isolation"
    description: str
    estimated_completion_minutes: int
    resources_involved: list[str]
    expected_outcome: str
    side_effects: list[str]     # e.g. ["evacuation congestion on N-5 Highway"]
 
class SimulationMetrics(BaseModel):
    response_time_improvement_pct: float
    population_protected: int
    roads_rerouted: int
    estimated_cost_pkr: float
    estimated_lives_protected: int
 
class BaselineComparison(BaseModel):
    """Required by evaluation criteria. Shows Amaan vs manual response."""
    baseline_response_time_minutes: float
    amaan_response_time_minutes: float
    baseline_false_positive_rate: float
    amaan_false_positive_rate: float
    baseline_resource_utilization_pct: float
    amaan_resource_utilization_pct: float
    improvement_summary: str
 
class SimulationResult(BaseModel):
    simulation_id: str
    before_state: CrisisState
    response_actions: list[ResponseAction]
    after_state: CrisisState
    metrics: SimulationMetrics
    baseline_comparison: BaselineComparison
    trace: dict
```
 
### Baseline Constants
 
**File:** `data/baseline_metrics.json`
 
```json
{
  "manual_dispatch_avg_minutes": 23,
  "manual_false_positive_rate": 0.23,
  "manual_resource_utilization": 0.65,
  "manual_contradiction_resolution_minutes": 45,
  "manual_response_coverage_pct": 0.45,
  "source": "Estimated from NDMA Annual Report 2023 and Pakistan emergency response literature"
}
```
 
### Scenario A Expected Simulation Output (Demo)

See [SCENARIOS.md](SCENARIOS.md) for the expected before/after simulation states and metric comparisons for Scenario A.
---

## AGENT 6 — StakeholderCommsAgent
 
**File:** `backend/agents/stakeholder_comms.py`
**Build order:** Sixth
**Evaluation relevance:** Impact Simulation + Stakeholder Coordination 15%
 
### Single Responsibility
 
Generate tailored alert messages for exactly 5 stakeholder groups.
Every message differs in language, tone, and technical depth.
Simulate delivery via Firebase Cloud Messaging (FCM).

### Antigravity Trace Must Include
- Each message generated with template used
- Personalization applied per stakeholder
- Delivery simulation log
- Fallback if FCM fails (store-and-forward)

### Input Model
 
```python
class StakeholderCommsInput(BaseModel):
    crisis: CrisisObject
    severity: SeverityPrediction
    allocation: AllocationPlan
    simulation: SimulationResult
```
 
### Output Model
 
```python
class StakeholderMessage(BaseModel):
    audience: str               # "public" | "emergency_services" | "hospital" |
                                # "utility" | "command_center"
    channel: str                # "fcm_push" | "sms_simulation" | "dashboard"
    language: str               # "urdu" | "english" | "bilingual"
    subject: str
    body: str
    urgency_level: str          # "info" | "warning" | "critical"
    sent_at: str                # ISO timestamp
 
class StakeholderCommsOutput(BaseModel):
    messages: list[StakeholderMessage]
    delivery_log: list[dict]        # simulated FCM confirmation per message
    trace: dict
```
 
### 5 Required Message Templates
 
**Audience 1 — General Public**
- Language: Bilingual (Urdu first, English below)
- Tone: Simple, calm, actionable
- Urgency: critical
```
سیلاب الرٹ — {sector} اسلام آباد
{sector} میں شدید بارش کی وجہ سے سیلاب کا خطرہ ہے۔
متاثرہ علاقوں کو فوری خالی کریں۔
قریبی شیلٹر: {shelter_address}
ہیلپ لائن: 1122
 
FLOOD ALERT — {sector} Islamabad
Flooding risk in {sector} due to heavy rainfall.
Evacuate affected streets immediately.
Nearest shelter: {shelter_address}
Helpline: 1122
```
 
**Audience 2 — Emergency Services (Rescue 1122)**
- Language: English
- Tone: Technical, action-oriented, structured
- Urgency: critical
```
DISPATCH ORDER — PRIORITY 1
Incident: {crisis_type}, {location}, Severity {severity}/5
Resources: {resources_summary}
Staging point: {staging_address}
ETA constraint: <{travel_time} minutes
Hospital pre-alerted: {hospital_name} ({beds} trauma beds prepared)
Coordinate: {coordination_note}
```
 
**Audience 3 — Hospital (PIMS / Polyclinic)**
- Language: English
- Tone: Clinical, capacity-focused
- Urgency: warning
```
PRE-ALERT: {hospital_name}
Potential {crisis_type} casualties incoming from {location}.
Severity estimate: Level {severity} — up to {max_casualties} casualties possible.
Prepare: {beds} trauma beds, {teams} emergency teams on standby.
ETA first patients: {eta_min}–{eta_max} minutes.
```
 
**Audience 4 — Utility Companies ( e.g. IESCO)**
- Language: English
- Tone: Technical, brief
- Urgency: warning
```
INFRASTRUCTURE ALERT — IESCO
Flood risk: {affected_sectors} sectors.
Recommended: Pre-emptive power isolation within {timeline} minutes.
Coordinate with NDMA before any isolation action.
NDMA Crisis Line: 1700
```
 
**Audience 5 — Command Center / Media**
- Language: English
- Tone: Formal briefing
- Urgency: info
```
INCIDENT BRIEF — AMAAN CRISIS INTELLIGENCE
Time: {timestamp}
Incident: {crisis_type}, {location}
Severity: {severity}/5 | Confidence: {confidence_pct}%
Affected population estimate: {population}
Resources deployed: {resources_summary}
Response time: {amaan_time} min (baseline: {baseline_time} min — {improvement}% faster)
Hospital status: {hospital_status}
Next update: 30 minutes
```
 
### Gemini Usage
 
Use Gemini to fill template variables from crisis data.
Temperature: 0.6 for natural language variation in public messages.
Temperature: 0.2 for technical messages (emergency services, hospital).
Always validate all required fields are present before sending.
---

## AGENT 7 — VerificationAgent
 
**File:** `backend/agents/verification.py`
**Build order:** Seventh
**Evaluation relevance:** Crisis Detection 25%, Robustness 10%
 
### Single Responsibility
 
Monitor active crises for new evidence that might update or contradict
the original classification. Trigger alert retraction when confidence
drops below 0.35. Generate correction notifications to all stakeholders.
Handle API failures gracefully with cached data fallback.

### Antigravity Trace Must Include
- Monitoring check results
- Confidence recalculation with new data
- Retraction decision logic (if triggered)
- Correction messages sent
- API failure handling log
- Post-incident summary

### Two Trigger Modes
 
**Mode 1 — Immediate (triggered by Orchestrator):**
Called when ClassificationAgent detects a contradiction.
Runs before pipeline continues to ResourceAllocationAgent.
Resolves whether to proceed or flag as unverified.
 
**Mode 2 — Monitoring (scheduled loop):**
Runs every 30 minutes for all active crises in Firestore.
Checks whether new signals update or overturn the classification.
Triggered by a FastAPI background task, not the main pipeline.
 
### Input Model
 
```python
class VerificationInput(BaseModel):
    crisis: CrisisObject
    new_signals: list[RawSignal]            # newly arrived signals to evaluate
    original_classification_trace: dict
    trigger_mode: str                       # "immediate" | "monitoring"
```
 
### Output Model
 
```python
class VerificationOutput(BaseModel):
    verdict: str                # "confirmed" | "updated" | "retracted" | "escalated"
    updated_crisis: CrisisObject | None     # populated if verdict is "updated"
    retraction_reason: str | None           # populated if verdict is "retracted"
    correction_messages: list[str]          # messages sent to all stakeholders
    confidence_delta: float                 # positive = more confident, negative = less
    trace: dict
```
 
### Retraction Logic
 
```python
def should_retract(
    self,
    original: CrisisObject,
    new_signals: list[RawSignal]
) -> bool:
    """
    Retract the crisis alert ONLY when ALL three conditions are met:
    1. New signal credibility > 0.75 (high-credibility source)
    2. New signal directly contradicts the current classification
    3. New signal timestamp is within 30 minutes (not stale)
    4. Updated confidence_score drops below 0.35
 
    NEVER retract based on a single anonymous signal.
    NEVER retract without at least one official or field-verified source.
    """
```
 
### Scenario B Demo — Required Output

See [SCENARIOS.md](SCENARIOS.md) for the exact retraction reasoning and updated crisis object expected for Scenario B.

### API Failure Degraded Mode
 
```python
def handle_degraded_mode(self, crisis_id: str) -> VerificationOutput:
    """
    When all APIs fail and no new signals can be fetched:
    - Maintain current classification (do not retract without evidence)
    - Set verdict = "confirmed" with explicit degraded note
    - Log degraded_mode = True in trace
    - Send alert to command center that manual field verification is needed
    - Pipeline continues — degraded mode never blocks emergency response
    """
    return VerificationOutput(
        verdict="confirmed",
        updated_crisis=None,
        retraction_reason=None,
        correction_messages=[
            "COMMAND CENTER: Amaan operating in degraded mode. "
            "All external APIs unavailable. Manual field verification "
            f"required for crisis {crisis_id}. Alert maintained until confirmed."
        ],
        confidence_delta=0.0,
        trace=self.log_trace(...)
    )
```
---

## AGENT 8 — ChatAgent
 
**File:** `backend/agents/chat_agent.py`
**Build order:** Last — independent pipeline, only after Agents 1–7 are complete and demo-ready
**Evaluation relevance:** Usability & UX 10%
 
### Single Responsibility
 
Answer citizen questions about nearby dangers, current crises, weather,
and safety in their preferred language (Urdu, Roman Urdu, or English).
Uses current crisis state from Firestore as real-time context.
Provide the "smart chat" feature visible in the React/Capacitor app demo.
Runs completely independently — not part of the crisis pipeline.

### Input Model
 
```python
class ChatInput(BaseModel):
    user_message: str
    user_location: dict             # {"lat": float, "lng": float}
    language_preference: str        # "urdu" | "english" | "roman_urdu" | "auto"
    conversation_history: list      # last 5 messages for context window
```
 
### Output Model
 
```python
class ChatOutput(BaseModel):
    response: str
    language_detected: str
    crisis_context_used: bool       # True if answer referenced active crisis data
    nearby_crises: list[str]        # crisis_ids within 10km of user location
    safety_actions: list[str]       # specific actions user should take right now
    trace: dict
```
 
### Language Detection Rules
 
```
User writes Urdu script (اردو characters) → respond in Urdu script
User writes Roman Urdu (e.g. "kya hal hai") → respond in Roman Urdu
User writes English → respond in English
User writes mixed → respond in Roman Urdu (most accessible for Pakistan)
 
Never switch language mid-response.
Keep all responses under 100 words — citizens need fast answers.
Always end with a specific action if any safety risk exists nearby.
```
 
### System Prompt Template
 
```python
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
- Keep responses under 100 words
- If any danger is nearby, always state what the user should do immediately
- Only use information provided above — never invent facts
- If you don't know something, say so clearly and give the 1122 helpline
- Be calm and factual — never cause panic
- If user asks about traffic, check crisis data for road blockages first
"""
```
### Sample Questions the Chat Must Handle
 
| User Input | Language | Expected Behavior |
|-----------|----------|------------------|
| `"Kya G-10 mein flooding hai abhi?"` | Roman Urdu | Check active crises, respond in Roman Urdu |
| `"What is the weather today?"` | English | Call Open-Meteo for user location |
| `"Nearest shelter kahan hai?"` | Roman Urdu | Query Firestore shelters collection |
| `"Is it safe to drive on Jinnah Avenue?"` | English | Check traffic + crisis road blocks |
| `"کیا میرے علاقے میں کوئی خطرہ ہے؟"` | Urdu | Respond in Urdu script with nearby crisis info |
| `"Koi alert hai kya aaj?"` | Roman Urdu | List active alerts near user location |

---

## AGENT TRACE EXPORT & API ENDPOINTS

See [DATA_FLOWS.md](DATA_FLOWS.md) for the final agent trace export format and the quick reference of all API endpoints.
