from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# =======================
# Signal Ingestion Agent
# =======================
class SignalIngestionInput(BaseModel):
    location: dict          # {"lat": 33.72, "lng": 73.04, "city": "Islamabad"}
    radius_km: float = 10.0
    time_window_hours: int = 2

class RawSignal(BaseModel):
    signal_id: str
    source: str             # "pmd" | "google_traffic" | "gdelt" | "citizen_app" | "mock"
    signal_type: str        # "weather" | "traffic" | "social" | "field_report"
    content: str
    location: dict
    timestamp: str
    credibility_score: float
    staleness_flag: bool
    raw_data: dict

class SignalIngestionOutput(BaseModel):
    signals: List[RawSignal]
    total_signals: int
    sources_contacted: List[str]
    sources_failed: List[str]
    fallback_used: bool
    trace: dict

# =======================
# Crisis Classification Agent
# =======================
class CrisisClassificationInput(BaseModel):
    signals: List[RawSignal]
    location: dict
    historical_context: dict

class CrisisObject(BaseModel):
    crisis_id: str
    crisis_type: str            # "urban_flood" | "heatwave" | "accident" | "power_outage" | "infrastructure" | "compound"
    sub_type: str
    location: dict
    confidence_score: float
    contradictions_detected: bool
    contradiction_detail: Optional[str]
    dominant_signals: List[str]
    dismissed_signals: List[str]
    status: str                 # "active" | "unverified" | "retracted"
    trace: dict

class CrisisClassificationOutput(BaseModel):
    primary_crisis: CrisisObject
    secondary_crisis: Optional[CrisisObject] = None
    classification_method: str
    trace: dict

# =======================
# Severity Prediction Agent
# =======================
class SeverityPredictionInput(BaseModel):
    crisis: CrisisObject
    weather_data: dict
    vulnerability_data: dict
    historical_events: list

class SeverityPrediction(BaseModel):
    severity_level: int             # 1 (minor) to 5 (catastrophic)
    severity_label: str
    affected_radius_km: float
    affected_population: int
    estimated_duration_hours: float
    peak_impact_time: str
    spread_risk: float
    cascading_risks: List[str]
    uncertainty_range: str
    trace: dict

# =======================
# Resource Allocation Agent
# =======================
class ResourceGroup(BaseModel):
    total: int
    available: int
    locations: List[dict]

class ShelterUnit(BaseModel):
    name: str
    capacity: int
    occupied: int
    location: dict

class ResourceInventory(BaseModel):
    ambulances: ResourceGroup
    rescue_boats: ResourceGroup
    rescue_teams: ResourceGroup
    police_traffic_units: ResourceGroup
    medical_outreach_teams: ResourceGroup
    water_tankers: ResourceGroup
    generators: ResourceGroup
    shelters: List[ShelterUnit]

class AllocationConstraints(BaseModel):
    budget_pkr: float = 500000.0
    max_travel_minutes: int = 30
    crew_shift_hours: int = 8

class ResourceAllocationInput(BaseModel):
    crises: List[CrisisObject]
    severity_predictions: List[SeverityPrediction]
    resource_inventory: ResourceInventory
    constraints: AllocationConstraints

class CrisisAllocation(BaseModel):
    crisis_id: str
    resources_assigned: dict
    dispatch_order: List[dict]
    justification: str

class AllocationPlan(BaseModel):
    plan_id: str
    crisis_allocations: List[CrisisAllocation]
    unmet_needs: List[str]
    trade_off_explanation: str
    total_resources_deployed: int
    estimated_cost_pkr: float
    fairness_check: str
    trace: dict

# =======================
# Simulation Agent
# =======================
class SimulationInput(BaseModel):
    crisis: CrisisObject
    severity: SeverityPrediction
    allocation: AllocationPlan

class CrisisState(BaseModel):
    population_at_risk: int
    roads_blocked: List[str]
    hospital_capacity_used_pct: float
    estimated_casualties_if_unaddressed: int
    response_coverage_pct: float

class ResponseAction(BaseModel):
    action_type: str
    description: str
    estimated_completion_minutes: int
    resources_involved: List[str]
    expected_outcome: str
    side_effects: List[str]

class SimulationMetrics(BaseModel):
    response_time_improvement_pct: float
    population_protected: int
    roads_rerouted: int
    estimated_cost_pkr: float
    estimated_lives_protected: int

class BaselineComparison(BaseModel):
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
    response_actions: List[ResponseAction]
    after_state: CrisisState
    metrics: SimulationMetrics
    baseline_comparison: BaselineComparison
    trace: dict

# =======================
# Stakeholder Comms Agent
# =======================
class StakeholderCommsInput(BaseModel):
    crisis: CrisisObject
    severity: SeverityPrediction
    allocation: AllocationPlan
    simulation: SimulationResult

class StakeholderMessage(BaseModel):
    audience: str
    channel: str
    language: str
    subject: str
    body: str
    urgency_level: str
    sent_at: str

class StakeholderCommsOutput(BaseModel):
    messages: List[StakeholderMessage]
    delivery_log: List[dict]
    trace: dict

# =======================
# Verification Agent
# =======================
class VerificationInput(BaseModel):
    crisis: CrisisObject
    new_signals: List[RawSignal]
    original_classification_trace: dict
    trigger_mode: str

class VerificationOutput(BaseModel):
    verdict: str
    updated_crisis: Optional[CrisisObject] = None
    retraction_reason: Optional[str] = None
    correction_messages: List[str]
    confidence_delta: float
    trace: dict

# =======================
# Chat Agent
# =======================
class ChatInput(BaseModel):
    user_message: str
    user_location: dict
    language_preference: str
    conversation_history: list

class ChatOutput(BaseModel):
    response: str
    language_detected: str
    crisis_context_used: bool
    nearby_crises: List[str]
    safety_actions: List[str]
    trace: dict
