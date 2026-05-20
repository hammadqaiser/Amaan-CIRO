"""
VerificationAgent — Handles contradictions, false alarms, retractions.
Build order: Seventh.
Evaluation relevance: Crisis Detection 25%, Robustness 10%.

Two trigger modes:
1. Immediate — called when ClassificationAgent detects contradiction (confidence < 0.50)
2. Monitoring — scheduled loop every 30 min for active crises
"""

import uuid
import json
from copy import deepcopy
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date

from agents.base_agent import BaseAgent
from models.schemas import (
    VerificationInput,
    VerificationOutput,
    CrisisObject,
    RawSignal
)

VERIFICATION_PROMPT = """
You are the Verification Agent for Amaan Crisis Intelligence System.
Review a previously classified crisis against new incoming signals.

Original Crisis:
{crisis}

Original Classification Reasoning:
{trace}

New Signals Received:
{new_signals}

Retraction rules (ALL must be met to retract):
1. New signal credibility > 0.75 (high-credibility source)
2. New signal directly contradicts the current classification
3. New signal timestamp is within 30 minutes (not stale)
4. Updated confidence_score would drop below 0.35

NEVER retract based on a single anonymous signal.
NEVER retract without at least one official or field-verified source.

Determine the verdict:
- "confirmed" — new signals support the original classification
- "updated" — classification needs modification but crisis is real
- "retracted" — crisis was a false alarm, retract all alerts
- "escalated" — crisis is worse than originally classified

Return ONLY this JSON:
{{
    "verdict": "string",
    "retraction_reason": "string or null",
    "correction_messages": ["string"],
    "confidence_delta": 0.0,
    "reasoning": "string"
}}
"""


class VerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="VerificationAgent")

    def _should_retract(self, original: CrisisObject, new_signals: list[RawSignal]) -> tuple[bool, str]:
        """
        Rule-based retraction check. Returns (should_retract, reason).
        Retract ONLY when ALL conditions from AGENTS.md are met.
        """
        now = datetime.now(timezone.utc)
        high_cred_contradictions = []

        for s in new_signals:
            # Check credibility > 0.75
            if s.credibility_score <= 0.75:
                continue

            # Check contradiction keywords
            is_contradiction = any(
                kw in s.content.lower()
                for kw in ["false alarm", "not a flood", "water main", "burst pipe",
                            "not real", "cancelled", "no danger", "safe now"]
            )
            if not is_contradiction:
                continue

            # Check freshness (within 30 minutes)
            try:
                sig_time = parse_date(s.timestamp)
                if sig_time.tzinfo is None:
                    sig_time = sig_time.replace(tzinfo=timezone.utc)
                age_minutes = (now - sig_time).total_seconds() / 60.0
                if age_minutes > 30:
                    continue
            except Exception:
                continue

            high_cred_contradictions.append(s)

        if not high_cred_contradictions:
            return False, None

        # Check if updated confidence would drop below 0.35
        # Each high-credibility contradiction reduces confidence by ~0.25
        projected_confidence = original.confidence_score - (0.25 * len(high_cred_contradictions))
        if projected_confidence < 0.35:
            reason = (
                f"Field verification (credibility {high_cred_contradictions[0].credibility_score:.2f}) "
                f"contradicts {original.crisis_type} classification. "
                f"Projected confidence: {projected_confidence:.2f} (below 0.35 threshold). "
                f"Source: {high_cred_contradictions[0].content}"
            )
            return True, reason

        return False, None

    def _rule_based_verify(self, crisis: CrisisObject, new_signals: list[RawSignal]) -> dict:
        """Deterministic fallback verification logic."""
        should_retract, reason = self._should_retract(crisis, new_signals)

        if should_retract:
            return {
                "verdict": "retracted",
                "retraction_reason": reason,
                "correction_messages": [
                    f"PUBLIC: Alert for {crisis.location.get('city', '')} has been cancelled. "
                    f"Situation has been reclassified. No evacuation required.",
                    f"RESCUE 1122: Stand down deployment. Reclassified as infrastructure incident.",
                    f"HOSPITAL: Cancel casualty preparation. False alarm confirmed."
                ],
                "confidence_delta": -(crisis.confidence_score - 0.10),
                "reasoning": reason
            }

        # Check for confirming signals
        confirming = [
            s for s in new_signals
            if s.credibility_score > 0.60 and not s.staleness_flag
            and any(kw in s.content.lower()
                    for kw in ["confirmed", "verified", "still ongoing", "worsening"])
        ]

        if confirming:
            return {
                "verdict": "confirmed",
                "retraction_reason": None,
                "correction_messages": [],
                "confidence_delta": min(0.15, 0.05 * len(confirming)),
                "reasoning": f"Crisis confirmed by {len(confirming)} new signal(s)"
            }

        # No strong evidence either way
        return {
            "verdict": "confirmed",
            "retraction_reason": None,
            "correction_messages": [],
            "confidence_delta": 0.0,
            "reasoning": "No new contradicting or confirming evidence. Maintaining current classification."
        }

    def handle_degraded_mode(self, crisis_id: str) -> VerificationOutput:
        """
        When all APIs fail and no new signals can be fetched.
        Maintains current classification — never retract without evidence.
        """
        trace_id = str(uuid.uuid4())
        trace = self.log_trace(
            trace_id=trace_id,
            input_data={"crisis_id": crisis_id, "mode": "degraded"},
            reasoning_steps=[
                "All external APIs unavailable",
                "Maintaining current classification (no evidence to retract)",
                "Requesting manual field verification"
            ],
            confidence_score=0.50,
            decision_made={"verdict": "confirmed", "degraded_mode": True},
            alternative_considered="Retraction considered but rejected — no evidence against current classification",
            fallback_triggered=True
        )

        return VerificationOutput(
            verdict="confirmed",
            updated_crisis=None,
            retraction_reason=None,
            correction_messages=[
                f"COMMAND CENTER: Amaan operating in degraded mode. "
                f"All external APIs unavailable. Manual field verification "
                f"required for crisis {crisis_id}. Alert maintained until confirmed."
            ],
            confidence_delta=0.0,
            trace=trace
        )

    async def run(self, input_data: VerificationInput) -> VerificationOutput:
        """Execute verification pipeline."""
        reasoning_steps = []
        reasoning_steps.append(f"Verification triggered in {input_data.trigger_mode} mode")
        reasoning_steps.append(f"Evaluating {len(input_data.new_signals)} new signals")

        # If no new signals, run degraded mode
        if not input_data.new_signals:
            reasoning_steps.append("No new signals available — running degraded mode check")
            return self.handle_degraded_mode(input_data.crisis.crisis_id)

        # Try Gemini first
        prompt = VERIFICATION_PROMPT.format(
            crisis=input_data.crisis.model_dump_json(),
            trace=json.dumps(input_data.original_classification_trace, default=str),
            new_signals=json.dumps([s.model_dump() for s in input_data.new_signals], default=str)
        )

        fallback = self._rule_based_verify(input_data.crisis, input_data.new_signals)
        gemini_out, fallback_triggered = self.call_gemini(prompt, fallback)

        if fallback_triggered:
            reasoning_steps.append("Used rule-based verification (Gemini unavailable)")
        else:
            reasoning_steps.append("Verification performed via Gemini LLM")

        verdict = gemini_out.get("verdict", fallback["verdict"])
        retraction_reason = gemini_out.get("retraction_reason", fallback["retraction_reason"])
        correction_messages = gemini_out.get("correction_messages", fallback["correction_messages"])
        confidence_delta = float(gemini_out.get("confidence_delta", fallback["confidence_delta"]))

        # Build updated crisis object
        updated_crisis = deepcopy(input_data.crisis)
        updated_crisis.confidence_score = max(0.0, min(1.0, updated_crisis.confidence_score + confidence_delta))

        if verdict == "retracted":
            updated_crisis.status = "retracted"
            updated_crisis.confidence_score = 0.0
            reasoning_steps.append(f"Crisis RETRACTED: {retraction_reason}")
        elif verdict == "confirmed":
            updated_crisis.status = "active"
            reasoning_steps.append(f"Crisis CONFIRMED. Confidence delta: {confidence_delta:+.2f}")
        elif verdict == "updated":
            updated_crisis.status = "active"
            reasoning_steps.append(f"Crisis UPDATED. New confidence: {updated_crisis.confidence_score:.2f}")
        elif verdict == "escalated":
            updated_crisis.status = "active"
            reasoning_steps.append(f"Crisis ESCALATED. Confidence delta: {confidence_delta:+.2f}")

        if gemini_out.get("reasoning"):
            reasoning_steps.append(f"Reasoning: {gemini_out['reasoning']}")

        trace_id = str(uuid.uuid4())
        trace = self.log_trace(
            trace_id=trace_id,
            input_data={
                "crisis_id": input_data.crisis.crisis_id,
                "trigger_mode": input_data.trigger_mode,
                "new_signal_count": len(input_data.new_signals)
            },
            reasoning_steps=reasoning_steps,
            confidence_score=updated_crisis.confidence_score,
            decision_made={
                "verdict": verdict,
                "confidence_delta": confidence_delta,
                "retracted": verdict == "retracted"
            },
            alternative_considered="Rule-based retraction check as fallback to LLM verification",
            fallback_triggered=fallback_triggered
        )

        return VerificationOutput(
            verdict=verdict,
            updated_crisis=updated_crisis,
            retraction_reason=retraction_reason,
            correction_messages=correction_messages,
            confidence_delta=confidence_delta,
            trace=trace
        )
