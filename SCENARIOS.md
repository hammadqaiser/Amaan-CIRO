# CIRO Demo Scenarios

This document details the expected outputs, data logic, and agent behaviors for the three primary hackathon demo scenarios.

## Scenario A — Primary Demo (G-10 Islamabad Flooding)

### Contradiction Detection Logic (CrisisClassificationAgent)
 
```
Signal A: "flooding in G-10" — credibility 0.87, timestamp: 14:32
Signal B: "water main burst, not flood" — credibility 0.40, timestamp: 10:00
 
Step 1: Timestamp gap = 4.5 hours → Signal B is stale (staleness_flag=True)
Step 2: Credibility gap = 0.47 → Signal A is significantly more reliable
Step 3: Resolution: dismiss Signal B
Step 4: contradiction_detail = "Field report (credibility 0.40, 4.5hrs stale)
         contradicts PMD+Traffic signals (credibility 0.87, current).
         Stale low-credibility report dismissed. Flood classification maintained."
Step 5: Confidence penalty for having any contradiction: -0.05 (minor reduction)
Step 6: Final confidence: 0.87 - 0.05 = 0.82 → well above 0.50 threshold
```

### Scenario A Expected Simulation Output (SimulationAgent)
 
```json
{
  "before_state": {
    "population_at_risk": 45000,
    "roads_blocked": ["Jinnah Avenue", "G-10 Markaz inner roads"],
    "hospital_capacity_used_pct": 0.78,
    "estimated_casualties_if_unaddressed": 120,
    "response_coverage_pct": 0.0
  },
  "response_actions": [
    {
      "action_type": "traffic_reroute",
      "description": "Reroute Jinnah Avenue traffic via 7th Avenue and Margalla Road",
      "estimated_completion_minutes": 12,
      "resources_involved": ["police_traffic_units: 3"],
      "expected_outcome": "Congestion reduced by 60%, emergency vehicle access restored",
      "side_effects": ["Increased load on 7th Avenue — monitor for secondary congestion"]
    },
    {
      "action_type": "dispatch_rescue",
      "description": "Deploy 4 rescue boats and 4 teams to G-10 Markaz",
      "estimated_completion_minutes": 8,
      "resources_involved": ["rescue_boats: 4", "rescue_teams: 4"],
      "expected_outcome": "Evacuation of flooded areas, estimated 2,000 residents assisted",
      "side_effects": []
    },
    {
      "action_type": "hospital_prealert",
      "description": "Pre-alert PIMS Hospital for incoming flood casualties",
      "estimated_completion_minutes": 3,
      "resources_involved": [],
      "expected_outcome": "12 trauma beds prepared, 4 emergency teams on standby",
      "side_effects": []
    },
    {
      "action_type": "public_alert",
      "description": "Send bilingual evacuation alert to G-10 residents via FCM",
      "estimated_completion_minutes": 1,
      "resources_involved": [],
      "expected_outcome": "Alert delivered to ~8,000 registered app users in G-10",
      "side_effects": ["Possible evacuation congestion on main exits if simultaneous"]
    }
  ],
  "after_state": {
    "population_at_risk": 12000,
    "roads_blocked": ["G-10 Markaz inner roads (partial)"],
    "hospital_capacity_used_pct": 0.85,
    "estimated_casualties_if_unaddressed": 28,
    "response_coverage_pct": 0.73
  },
  "metrics": {
    "response_time_improvement_pct": 65.2,
    "population_protected": 33000,
    "roads_rerouted": 2,
    "estimated_cost_pkr": 187000,
    "estimated_lives_protected": 92
  },
  "baseline_comparison": {
    "baseline_response_time_minutes": 23.0,
    "amaan_response_time_minutes": 8.0,
    "baseline_false_positive_rate": 0.23,
    "amaan_false_positive_rate": 0.06,
    "baseline_resource_utilization_pct": 0.65,
    "amaan_resource_utilization_pct": 0.91,
    "improvement_summary": "Amaan reduced response time by 65% (23 min → 8 min), cut false positives by 74%, and improved resource utilization by 40% compared to manual dispatch baseline."
  }
}
```

## Scenario B — False Alarm Recovery (G-10 Water Main Burst)

### Scenario B Demo — Required Output (VerificationAgent)
 
This agent must produce exactly this output for the false alarm demo:
 
```json
{
  "verdict": "retracted",
  "retraction_reason": "Field verification (credibility 0.80, 5 minutes ago) confirmed water main burst at G-10/2. Original PMD rainfall signal remains valid but applies to adjacent G-10/3. Flooding classification was location-mismatched. Reclassifying as infrastructure incident.",
  "correction_messages": [
    "PUBLIC: Flood alert for G-10/2 has been cancelled. Situation is a water main burst being repaired by IESCO. No evacuation required. We apologize for the concern caused.",
    "RESCUE 1122: Stand down flood deployment to G-10/2. Reclassified as water main infrastructure incident. 2 teams remain for safety cordon only.",
    "PIMS Hospital: Cancel flood casualty preparation for G-10/2. Maintain 2 beds on general standby. False alarm confirmed."
  ],
  "confidence_delta": -0.54,
  "updated_crisis": {
    "crisis_type": "infrastructure",
    "sub_type": "water_main_burst",
    "confidence_score": 0.88,
    "status": "active"
  }
}
```

## Scenario C — Dual Crisis (G-10 Flood + I-8 Heatwave)

### Scenario C Demo Expected Output (ResourceAllocationAgent)
 
```json
{
  "crisis_allocations": [
    {
      "crisis_id": "flood-g10-001",
      "resources_assigned": {
        "rescue_boats": 4,
        "rescue_teams": 4,
        "police_traffic_units": 3,
        "ambulances": 2
      },
      "justification": "G-10 flood has impact score 187,200 (severity 4, 45,000 population, spread risk 0.83). Highest priority. All available rescue boats allocated here."
    },
    {
      "crisis_id": "heat-i8-001",
      "resources_assigned": {
        "medical_outreach_teams": 2,
        "ambulances": 2,
        "water_tankers": 1
      },
      "justification": "I-8 heatwave has impact score 58,900 (severity 2, 12,000 population). Lower severity but low-income flag adds 15% fairness bonus to priority. Medical outreach assigned."
    }
  ],
  "trade_off_explanation": "All 4 rescue boats went to G-10 flooding because it affects 45,000 people at critical severity. I-8 gets medical and water teams for the heatwave — no boats were available, but the crisis type doesn't need them. The remaining 2 ambulances are on standby for either location.",
  "fairness_check": "I-8 is a low-income sector and received medical outreach coverage proportional to its impact score with the 15% fairness bonus applied. No deprioritization detected."
}
```
