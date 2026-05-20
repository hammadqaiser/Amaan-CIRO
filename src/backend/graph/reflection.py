"""
Reflection — Classification ⇄ Verification reflection loop.

Mirrors SlashAgents' graph/reflection.py debate pattern.
When VerificationAgent finds issues, it generates a critique
that gets fed back to ClassificationAgent for re-evaluation.

Max 2 iterations to prevent infinite loops.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CIROReflector:
    """Handles the Classification ⇄ Verification reflection loop."""

    def reflect_on_classification(
        self,
        state: Dict[str, Any],
        verification_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate critique from verification for classification to revise.

        Called after VerificationAgent runs. If the verdict is not "confirmed"
        and not "retracted", produce a critique string that ClassificationAgent
        will see in its next invocation via historical_context.

        Returns updated verification_debate state.
        """
        debate = state.get("verification_debate", {
            "classification_history": "",
            "verification_history": "",
            "critique": "",
            "iteration_count": 0,
            "resolved": False,
        })

        verdict = verification_output.get("verdict", "confirmed")
        confidence_delta = verification_output.get("confidence_delta", 0)
        retraction_reason = verification_output.get("retraction_reason", "")

        iteration = debate.get("iteration_count", 0) + 1

        if verdict == "retracted":
            return {
                **debate,
                "resolved": True,
                "iteration_count": iteration,
                "verification_history": (
                    debate.get("verification_history", "") +
                    f"\nIteration {iteration}: RETRACTED — {retraction_reason}"
                ),
            }

        if verdict == "confirmed":
            return {
                **debate,
                "resolved": True,
                "iteration_count": iteration,
                "verification_history": (
                    debate.get("verification_history", "") +
                    f"\nIteration {iteration}: CONFIRMED"
                ),
            }

        # verdict is "updated" or "escalated" — generate critique
        critique = (
            f"[Reflection Iteration {iteration}] "
            f"Verification verdict: {verdict}. "
            f"Confidence delta: {confidence_delta:+.3f}. "
        )

        if retraction_reason:
            critique += f"Reason: {retraction_reason}. "

        correction_msgs = verification_output.get("correction_messages", [])
        if correction_msgs:
            critique += f"Corrections suggested: {'; '.join(correction_msgs[:2])}. "

        critique += "Re-evaluate classification considering this new evidence."

        logger.info(f"[Reflector] Generated critique (iter {iteration}): {critique[:100]}...")

        return {
            **debate,
            "critique": critique,
            "iteration_count": iteration,
            "resolved": False,
            "verification_history": (
                debate.get("verification_history", "") +
                f"\nIteration {iteration}: {verdict} — critique generated"
            ),
        }

    def extract_lesson(self, final_state: Dict[str, Any]) -> str:
        """
        After pipeline completes, extract a lesson from the reflection loop.
        Stored for future reference (similar to SlashAgents' memory system).
        """
        debate = final_state.get("verification_debate", {})
        iterations = debate.get("iteration_count", 0)

        if iterations == 0:
            return "No verification loop triggered — classification was confident."

        crisis = final_state.get("crisis_object", {})
        return (
            f"Classification required {iterations} verification iteration(s). "
            f"Final crisis type: {crisis.get('crisis_type', 'unknown')}. "
            f"Final confidence: {crisis.get('confidence_score', 0):.2f}. "
            f"History: {debate.get('verification_history', 'none')}"
        )
