# Demo Scenarios

This document details the expected outputs, data logic, and agent behaviors for the three primary demo scenarios shipped with Amaan CIRO.

---

## Scenario A — Urban Flooding (G-10 Islamabad)

### Signal Contradiction Resolution

The CrisisClassificationAgent receives 5 simultaneous signals. One contradicts the others:

```
Signal A: "flooding in G-10" — credibility 0.87, timestamp: 14:32 (current)
Signal B: "water main burst, not flood" — credibility 0.40, timestamp: 10:00 (stale)

Step 1: Timestamp gap = 4.5 hours → Signal B is stale (staleness_flag=True)
Step 2: Credibility gap = 0.47 → Signal A is significantly more reliable
Step 3: Resolution — dismiss Signal B
Step 4: Contradiction detail logged:
        "Field report (credibility 0.40, 4.5hrs stale) contradicts PMD+Traffic
         signals (credibility 0.87, current). Dismissed due to low credibility
         and staleness. Flood classification maintained."
Step 5: Confidence penalty for having any contradiction: -0.05
Step 6: Final confidence: 0.87 - 0.05 = 0.82 → above 0.50 threshold → status: active
```

### Simulation Output

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
      "expected_outcome": "Evacuation of flooded areas, ~2,000 residents assisted"
    },
    {
      "action_type": "hospital_prealert",
      "description": "Pre-alert PIMS Hospital for incoming flood casualties",
      "estimated_completion_minutes": 3,
      "expected_outcome": "12 trauma beds prepared, 4 emergency teams on standby"
    },
    {
      "action_type": "public_alert",
      "description": "Send bilingual evacuation alert to G-10 residents",
      "estimated_completion_minutes": 1,
      "expected_outcome": "Alert delivered to ~8,000 registered users in G-10"
    }
  ],
  "after_state": {
    "population_at_risk": 12000,
    "roads_blocked": ["G-10 Markaz inner roads (partial)"],
    "hospital_capacity_used_pct": 0.85,
    "estimated_casualties_if_unaddressed": 28,
    "response_coverage_pct": 0.73
  },
  "baseline_comparison": {
    "baseline_response_time_minutes": 23.0,
    "amaan_response_time_minutes": 8.0,
    "improvement_summary": "Response time reduced by 65% (23 min → 8 min), false positives cut by 74%, resource utilization improved by 40%."
  }
}
```

---

## Scenario B — False Alarm Recovery

A low-confidence flood signal triggers classification. Field verification confirms it was a water main burst, not a flood. The VerificationAgent retracts the crisis.

### Verification Output

```json
{
  "verdict": "retracted",
  "retraction_reason": "Field verification (credibility 0.80, 5 minutes ago) confirmed water main burst at G-10/2. Original PMD rainfall signal remains valid but applies to adjacent G-10/3. Flooding classification was location-mismatched. Reclassifying as infrastructure incident.",
  "correction_messages": [
    "PUBLIC: Flood alert for G-10/2 has been cancelled. Situation is a water main burst being repaired by IESCO. No evacuation required.",
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

---

## Scenario C — Dual Crisis Coordination (G-10 Flood + I-8 Heatwave)

Two crises are active simultaneously. The ResourceAllocationAgent must split constrained resources and explain every trade-off.

### Resource Allocation Output

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
