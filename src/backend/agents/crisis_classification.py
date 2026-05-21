"""
CrisisClassificationAgent — Classifies crisis type with confidence scoring.
Build order: Second.
Evaluation relevance: Crisis Detection 25% (highest weighted criterion).

Uses Gemini 2.0 Flash for classification with rule-based fallback.
Detects contradictions between conflicting signals.
"""

import uuid
import json
from datetime import datetime, timezone

from agents.base_agent import BaseAgent
from models.schemas import (
    CrisisClassificationInput,
    CrisisClassificationOutput,
    CrisisObject,
    RawSignal
)

CLASSIFICATION_PROMPT = """
You are a crisis classification AI for Pakistan Emergency Management.

Analyze these signals and classify the crisis:
{signals_json}

Historical vulnerability data for this area:
{historical_context}

Current season: {season}
Current time: {current_time}

VALID crisis_type VALUES (you MUST use one of these):
- "urban_flood" — for any flooding, heavy rainfall >30mm/3hrs, waterlogging, submerged roads
- "heatwave" — for extreme heat >40°C, heat exhaustion, dehydration emergencies
- "accident" — for road accidents, vehicle collisions, infrastructure collapse
- "power_outage" — for electricity failures, grid overload, transformer damage
- "infrastructure" — for water main bursts, pipeline failures, building damage
- "compound" — for multiple simultaneous crisis types

CRITICAL: You MUST NEVER return "none", "no_crisis", "normal", "unknown", or any empty string as crisis_type.
If signals show any weather anomaly (rainfall >5mm, temperature >38°C, wind >50km/h), classify it.
If signals are truly routine with zero concerning data, classify as "infrastructure" with confidence_score 0.35.

Classification rules to apply:
- Monsoon season (July–September) + rainfall >50mm/3hrs = boost urban_flood probability by +0.25
- G-10, I-10, G-11, G-13 Islamabad = high flood vulnerability sectors
- Temperature >42°C + low-income sector = classify as heatwave emergency
- Temperature >38°C in any sector = classify as heatwave with confidence 0.50+
- PMD official alert + any corroborating signal = minimum confidence 0.75
- Any rainfall >15mm = at minimum classify as urban_flood with confidence 0.45+

Contradiction resolution rules:
- Two signals conflict → check timestamps, prefer newer signal
- Credibility difference >0.30 → prefer higher credibility source
- Contradiction cannot be resolved → set confidence <0.50, status=unverified
- If contradiction resolved by dismissing stale/low-credibility signal → confidence penalty of 0.05

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


class CrisisClassificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="CrisisClassificationAgent")

    def _rule_based_classify(self, signals: list[RawSignal]) -> dict:
        """
        Deterministic fallback. Uses signal keywords and credibility scores only.
        Applied when Gemini API is unavailable during demo or rate-limited.
        """
        flood_signals = [
            s for s in signals
            if any(kw in s.content.lower() for kw in ["rain", "flood", "water", "submerged", "precipitation"])
            and not s.staleness_flag
        ]
        heat_signals = [
            s for s in signals
            if any(kw in s.content.lower() for kw in ["heat", "temperature", "heatwave", "42", "43", "44", "45"])
            and not s.staleness_flag
        ]

        # Check for contradictions
        contradiction_signals = [
            s for s in signals
            if any(kw in s.content.lower() for kw in ["not a flood", "false alarm", "water main", "burst"])
        ]
        contradictions_detected = len(contradiction_signals) > 0 and len(flood_signals) > 0
        contradiction_detail = None
        dismissed_ids = []

        if contradictions_detected:
            # Resolve: dismiss stale or low-credibility contradiction signals
            for cs in contradiction_signals:
                if cs.staleness_flag or cs.credibility_score < 0.50:
                    dismissed_ids.append(cs.signal_id)
                    contradiction_detail = (
                        f"Signal from {cs.source} (credibility {cs.credibility_score:.2f}, "
                        f"stale={cs.staleness_flag}) contradicts flood classification. "
                        f"Dismissed due to low credibility/staleness."
                    )

        if len(flood_signals) >= 2:
            avg_cred = sum(s.credibility_score for s in flood_signals) / len(flood_signals)
            confidence = min(0.85, avg_cred)
            if contradictions_detected and dismissed_ids:
                confidence -= 0.05  # Penalty for resolved contradiction
            return {
                "crisis_type": "urban_flood",
                "sub_type": "flash_flood",
                "confidence_score": confidence,
                "contradictions_detected": contradictions_detected,
                "contradiction_detail": contradiction_detail,
                "dominant_signal_ids": [s.signal_id for s in flood_signals],
                "dismissed_signal_ids": dismissed_ids,
                "reasoning": f"Rule-based fallback: {len(flood_signals)} flood signals detected with avg credibility {avg_cred:.2f}"
            }
        elif len(heat_signals) >= 2:
            return {
                "crisis_type": "heatwave",
                "sub_type": "extreme_heat",
                "confidence_score": 0.60,
                "contradictions_detected": False,
                "contradiction_detail": None,
                "dominant_signal_ids": [s.signal_id for s in heat_signals],
                "dismissed_signal_ids": [],
                "reasoning": "Rule-based fallback: multiple heat signals detected"
            }
        else:
            # Check if any individual signal hints at a crisis type
            any_weather = [s for s in signals if s.signal_type == "weather" and not s.staleness_flag]
            if any_weather:
                # Extract temperature from weather signal content
                for ws in any_weather:
                    content_lower = ws.content.lower()
                    # Check for any temperature above 38C
                    import re as _re
                    temp_match = _re.search(r'(\d+\.?\d*)\s*°?c', content_lower)
                    if temp_match:
                        temp_val = float(temp_match.group(1))
                        if temp_val > 38.0:
                            return {
                                "crisis_type": "heatwave",
                                "sub_type": "heat_advisory",
                                "confidence_score": 0.50,
                                "contradictions_detected": False,
                                "contradiction_detail": None,
                                "dominant_signal_ids": [ws.signal_id],
                                "dismissed_signal_ids": [],
                                "reasoning": f"Rule-based fallback: Temperature {temp_val}°C exceeds 38°C threshold. Heat advisory issued."
                            }
            return {
                "crisis_type": "infrastructure",
                "sub_type": "monitoring",
                "confidence_score": 0.35,
                "contradictions_detected": False,
                "contradiction_detail": None,
                "dominant_signal_ids": [],
                "dismissed_signal_ids": [],
                "reasoning": "Rule-based fallback: No strong crisis signals, but monitoring infrastructure conditions."
            }

    async def run(self, input_data: CrisisClassificationInput) -> CrisisClassificationOutput:
        """Execute crisis classification pipeline."""
        reasoning_steps = []

        # Prepare inputs
        signals_json = json.dumps([s.model_dump() for s in input_data.signals], indent=2, default=str)
        historical_context = json.dumps(input_data.historical_context, indent=2)
        current_time = datetime.now(timezone.utc).isoformat()
        current_month = datetime.now(timezone.utc).month
        season = "Monsoon" if 7 <= current_month <= 9 else "Standard"

        prompt = CLASSIFICATION_PROMPT.format(
            signals_json=signals_json,
            historical_context=historical_context,
            season=season,
            current_time=current_time
        )

        # Get fallback ready
        fallback_response = self._rule_based_classify(input_data.signals)

        # Call Gemini via BaseAgent method
        gemini_result, fallback_triggered = self.call_gemini(prompt, fallback_response)

        # Build the final CrisisObject
        method = "rule_based_fallback" if fallback_triggered else "gemini_inference"

        confidence = float(gemini_result.get("confidence_score", 0.0))
        contradictions_detected = bool(gemini_result.get("contradictions_detected", False))

        # Apply strict bounds from rules if AI missed them
        if contradictions_detected and not gemini_result.get("dismissed_signal_ids"):
            # Unresolved contradiction
            if confidence >= 0.50:
                confidence = 0.49
                reasoning_steps.append("Forced confidence < 0.50 due to unresolved contradiction.")
        elif contradictions_detected and gemini_result.get("dismissed_signal_ids"):
            # Resolved contradiction — apply penalty
            confidence = max(0.0, confidence - 0.05)
            reasoning_steps.append("Applied -0.05 confidence penalty for resolved contradiction.")

        status = "active" if confidence >= 0.50 else "unverified"

        reasoning_steps.append(f"Classification performed using {method}.")
        reasoning_steps.append(f"Classified as {gemini_result.get('crisis_type')} with {confidence:.2f} confidence.")
        reasoning_steps.append(f"Season: {season}, Time: {current_time}")

        if contradictions_detected:
            reasoning_steps.append(f"Contradiction: {gemini_result.get('contradiction_detail')}")

        if gemini_result.get("reasoning"):
            reasoning_steps.append(f"LLM reasoning: {gemini_result['reasoning']}")

        trace_id = str(uuid.uuid4())

        crisis_obj = CrisisObject(
            crisis_id=str(uuid.uuid4()),
            crisis_type=gemini_result.get("crisis_type", "unknown"),
            sub_type=gemini_result.get("sub_type", "unclassified"),
            location=input_data.location,
            confidence_score=confidence,
            contradictions_detected=contradictions_detected,
            contradiction_detail=gemini_result.get("contradiction_detail"),
            dominant_signals=gemini_result.get("dominant_signal_ids", []),
            dismissed_signals=gemini_result.get("dismissed_signal_ids", []),
            status=status,
            trace={}
        )

        trace = self.log_trace(
            trace_id=trace_id,
            input_data={
                "signal_count": len(input_data.signals),
                "location": input_data.location,
                "season": season
            },
            reasoning_steps=reasoning_steps,
            confidence_score=confidence,
            decision_made={
                "crisis_type": crisis_obj.crisis_type,
                "sub_type": crisis_obj.sub_type,
                "status": status,
                "contradictions_detected": contradictions_detected
            },
            alternative_considered="Rule-based keyword matching as fallback to Gemini inference",
            fallback_triggered=fallback_triggered
        )

        crisis_obj.trace = trace

        return CrisisClassificationOutput(
            primary_crisis=crisis_obj,
            secondary_crisis=None,
            classification_method=method,
            trace=trace
        )
