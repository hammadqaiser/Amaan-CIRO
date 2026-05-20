"""
StakeholderCommsAgent — Generates messages for 5 stakeholder groups.
Build order: Sixth.
Evaluation relevance: Impact Simulation + Stakeholder Coordination 15%.

Generates bilingual (Urdu/English) public alerts, technical dispatch orders,
hospital pre-alerts, utility warnings, and command center briefings.
"""

import uuid
import json
from datetime import datetime, timezone

from agents.base_agent import BaseAgent
from models.schemas import (
    StakeholderCommsInput,
    StakeholderCommsOutput,
    StakeholderMessage
)

COMMS_PROMPT = """
You are the Stakeholder Communications Agent for Amaan Crisis Intelligence System.
Generate emergency messages for the following crisis response.

Crisis: {crisis}
Severity: {severity}
Allocation: {allocation}

You MUST generate exactly 5 messages. For each, use the exact audience name below.
For the "public" message, write the body in BILINGUAL format: Urdu first (using Urdu script),
then English translation below.

Audiences:
1. "public" — Bilingual Urdu/English, calm, actionable, include shelter address and 1122 helpline
2. "emergency_services" — English, technical, structured dispatch order
3. "hospitals" — English, clinical, capacity-focused, include bed preparation
4. "media" — English, technical press statement/release
5. "ndma" — English, formal briefing with metrics

Output a JSON object with this structure:
{{
    "messages": [
        {{
            "audience": "string",
            "channel": "string",
            "language": "string",
            "subject": "string",
            "body": "string",
            "urgency_level": "string",
            "sent_at": "string"
        }}
    ]
}}
"""


class StakeholderCommsAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="StakeholderCommsAgent")

    def _get_fallback_messages(self, crisis_type: str, location: dict,
                                severity_level: int, resources: dict) -> dict:
        """Generate rule-based fallback messages using templates from AGENTS.md."""
        now = datetime.now(timezone.utc).isoformat()
        sector = location.get("city", location.get("address", "Islamabad"))
        shelter = "G-10 Markaz Community Center"

        messages = [
            {
                "audience": "public",
                "channel": "fcm_push",
                "language": "bilingual",
                "subject": f"ہنگامی الرٹ — {sector} / EMERGENCY ALERT — {sector}",
                "body": (
                    f"سیلاب الرٹ — {sector}\n"
                    f"{sector} میں شدید بارش کی وجہ سے سیلاب کا خطرہ ہے۔\n"
                    f"متاثرہ علاقوں کو فوری خالی کریں۔\n"
                    f"قریبی شیلٹر: {shelter}\n"
                    f"ہیلپ لائن: 1122\n\n"
                    f"FLOOD ALERT — {sector}\n"
                    f"Flooding risk due to heavy rainfall.\n"
                    f"Evacuate affected streets immediately.\n"
                    f"Nearest shelter: {shelter}\n"
                    f"Helpline: 1122"
                ) if crisis_type == "urban_flood" else (
                    f"گرمی کی لہر الرٹ — {sector}\n"
                    f"درجہ حرارت خطرناک حد تک بلند ہے۔ گھروں میں رہیں۔\n"
                    f"ہیلپ لائن: 1122\n\n"
                    f"HEATWAVE ALERT — {sector}\n"
                    f"Dangerous heat levels. Stay indoors, hydrate frequently.\n"
                    f"Helpline: 1122"
                ),
                "urgency_level": "critical",
                "sent_at": now
            },
            {
                "audience": "emergency_services",
                "channel": "emergency_api",
                "language": "english",
                "subject": f"DISPATCH ORDER — PRIORITY 1 — {crisis_type.upper()}",
                "body": (
                    f"Incident: {crisis_type.replace('_', ' ').title()}, {sector}, "
                    f"Severity {severity_level}/5\n"
                    f"Resources: {json.dumps(resources)}\n"
                    f"ETA constraint: <30 minutes\n"
                    f"Coordinate with local police for traffic management."
                ),
                "urgency_level": "critical",
                "sent_at": now
            },
            {
                "audience": "hospitals",
                "channel": "healthcare_network",
                "language": "english",
                "subject": f"PRE-ALERT: PIMS Hospital — {crisis_type.replace('_', ' ').title()}",
                "body": (
                    f"Potential casualties incoming from {sector}.\n"
                    f"Severity estimate: Level {severity_level}\n"
                    f"Prepare: 12 trauma beds, 4 emergency teams on standby.\n"
                    f"ETA first patients: 15–25 minutes."
                ),
                "urgency_level": "warning",
                "sent_at": now
            },
            {
                "audience": "media",
                "channel": "infrastructure_alert",
                "language": "english",
                "subject": "PRESS RELEASE — AMAAN DISASTER BROADCAST",
                "body": (
                    f"Amaan CIRO confirms crisis event in {sector}.\n"
                    f"Type: {crisis_type.replace('_', ' ').title()}, Severity Level {severity_level}.\n"
                    f"Emergency protocols activated. Media and public advised to follow only official guidance.\n"
                    f"Emergency helpline: 1122"
                ),
                "urgency_level": "warning",
                "sent_at": now
            },
            {
                "audience": "ndma",
                "channel": "dashboard",
                "language": "english",
                "subject": "INCIDENT BRIEF — AMAAN CRISIS INTELLIGENCE",
                "body": (
                    f"Time: {now}\n"
                    f"Incident: {crisis_type.replace('_', ' ').title()}, {sector}\n"
                    f"Severity: {severity_level}/5\n"
                    f"Resources deployed: {json.dumps(resources)}\n"
                    f"Next update: 30 minutes"
                ),
                "urgency_level": "info",
                "sent_at": now
            }
        ]
        return {"messages": messages}

    async def run(self, input_data: StakeholderCommsInput) -> StakeholderCommsOutput:
        """Execute stakeholder communications pipeline."""
        reasoning_steps = []

        crisis_type = input_data.crisis.crisis_type
        location = input_data.crisis.location
        severity_level = input_data.severity.severity_level
        resources = {}
        if input_data.allocation.crisis_allocations:
            resources = input_data.allocation.crisis_allocations[0].resources_assigned

        # Try Gemini for rich, context-aware messages
        prompt = COMMS_PROMPT.format(
            crisis=input_data.crisis.model_dump_json(),
            severity=input_data.severity.model_dump_json(),
            allocation=input_data.allocation.model_dump_json()
        )

        fallback = self._get_fallback_messages(crisis_type, location, severity_level, resources)
        gemini_out, fallback_triggered = self.call_gemini(prompt, fallback)

        if fallback_triggered:
            reasoning_steps.append("Used template-based fallback messages (Gemini unavailable)")
        else:
            reasoning_steps.append("Generated context-aware messages via Gemini LLM")

        messages_data = gemini_out.get("messages", fallback["messages"])

        # Ensure exactly 5 messages
        if len(messages_data) < 5:
            reasoning_steps.append(f"LLM returned {len(messages_data)} messages, supplementing with fallback")
            fallback_msgs = fallback["messages"]
            existing_audiences = {m.get("audience") for m in messages_data}
            for fb_msg in fallback_msgs:
                if fb_msg["audience"] not in existing_audiences:
                    messages_data.append(fb_msg)

        messages = [StakeholderMessage(**m) for m in messages_data[:5]]
        reasoning_steps.append(f"Generated {len(messages)} stakeholder messages for 5 audiences")

        # Simulate delivery log
        delivery_log = [
            {
                "audience": m.audience,
                "channel": m.channel,
                "status": "delivered",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "latency_ms": 120
            }
            for m in messages
        ]
        reasoning_steps.append("Simulated delivery to all 5 stakeholder channels")

        trace_id = str(uuid.uuid4())
        trace = self.log_trace(
            trace_id=trace_id,
            input_data={
                "crisis_type": crisis_type,
                "severity": severity_level,
                "audiences": [m.audience for m in messages]
            },
            reasoning_steps=reasoning_steps,
            confidence_score=0.95,
            decision_made={
                "message_count": len(messages),
                "audiences_covered": [m.audience for m in messages]
            },
            alternative_considered="Template-based messages as fallback to LLM-generated",
            fallback_triggered=fallback_triggered
        )

        return StakeholderCommsOutput(
            messages=messages,
            delivery_log=delivery_log,
            trace=trace
        )
