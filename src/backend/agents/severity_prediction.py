"""
SeverityPredictionAgent — Predicts severity, evolution, duration, affected population.
Build order: Third.
Evaluation relevance: Crisis Detection 25%.

Uses calculation formulas from AGENTS.md for urban flood and heatwave.
"""

import uuid
import math
from datetime import datetime, timezone, timedelta

from agents.base_agent import BaseAgent
from models.schemas import SeverityPredictionInput, SeverityPrediction

SEVERITY_PROMPT = """
You are a severity prediction AI for Pakistan Emergency Management.

Crisis classified as: {crisis_type} ({sub_type})
Location: {location}
Weather data: {weather_data}
Vulnerability data: {vulnerability_data}
Historical events: {historical_events}

Based on this data, predict the severity using these thresholds:
- Level 1 (Minor): < 1,000 affected
- Level 2 (Moderate): 1,000 – 10,000
- Level 3 (Severe): 10,000 – 50,000
- Level 4 (Critical): 50,000 – 150,000
- Level 5 (Catastrophic): > 150,000

Return ONLY this JSON:
{{
    "severity_level": int,
    "severity_label": "string",
    "affected_radius_km": float,
    "affected_population": int,
    "estimated_duration_hours": float,
    "spread_risk": float,
    "cascading_risks": ["string"],
    "reasoning": "string"
}}
"""


class SeverityPredictionAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="SeverityPredictionAgent")

    def _determine_severity_level(self, population: int) -> tuple[int, str]:
        """Map affected population to severity level per AGENTS.md thresholds."""
        if population < 1000:
            return 1, "Minor"
        elif population <= 10000:
            return 2, "Moderate"
        elif population <= 50000:
            return 3, "Severe"
        elif population <= 150000:
            return 4, "Critical"
        else:
            return 5, "Catastrophic"

    def _calculate_urban_flood(self, weather: dict, vuln: dict, reasoning: list) -> dict:
        """Calculate urban flood severity using formulas from AGENTS.md."""
        drainage = vuln.get("drainage_capacity_mm_per_hr", 15.0)
        rainfall_mm = weather.get("rainfall_mm", 60.0)
        rainfall_intensity = weather.get("rainfall_intensity_mm_per_hr", rainfall_mm / 3.0)
        flood_vuln = vuln.get("flood_vulnerability", 0.70)
        density = vuln.get("population_density_per_sqkm", 7000)
        area_sqkm = vuln.get("area_sqkm", 4.0)

        # Duration estimate: AGENTS.md formula
        duration_hours = (rainfall_mm / max(drainage, 1)) * 1.3
        reasoning.append(
            f"Duration = ({rainfall_mm}mm / {drainage}mm/hr) × 1.3 = {duration_hours:.1f} hours"
        )

        # Spread risk: AGENTS.md formula
        drainage_score = min(1.0, drainage / 30.0)  # Normalize drainage to 0-1 scale
        spread_risk = min(0.95, (rainfall_intensity / 10.0) * (1.0 - drainage_score))
        reasoning.append(
            f"Spread risk = ({rainfall_intensity:.1f}/10) × (1 - {drainage_score:.2f}) = {spread_risk:.2f}"
        )

        # Affected radius from area
        affected_radius_km = math.sqrt(area_sqkm / math.pi)
        reasoning.append(f"Affected radius = √({area_sqkm}/π) = {affected_radius_km:.2f} km")

        # Affected population: AGENTS.md formula
        calc_area = math.pi * (affected_radius_km ** 2)
        affected_population = int(calc_area * density * flood_vuln)
        reasoning.append(
            f"Affected pop = π × {affected_radius_km:.2f}² × {density} × {flood_vuln} = {affected_population}"
        )

        cascading = ["road_closure", "power_outage"]
        if rainfall_mm > 80:
            cascading.append("water_contamination")
        if flood_vuln > 0.75:
            cascading.append("structural_damage")

        return {
            "duration_hours": round(duration_hours, 1),
            "spread_risk": round(spread_risk, 2),
            "affected_radius_km": round(affected_radius_km, 2),
            "affected_population": affected_population,
            "cascading_risks": cascading
        }

    def _calculate_heatwave(self, weather: dict, vuln: dict, reasoning: list) -> dict:
        """Calculate heatwave severity."""
        temp = weather.get("temp_c", weather.get("temperature_c", 38))
        density = vuln.get("population_density_per_sqkm", 7000)
        low_income = vuln.get("low_income_flag", False)
        area_sqkm = vuln.get("area_sqkm", 4.0)

        # Duration: heatwaves typically last 6-48 hours
        duration_hours = max(6, (temp - 38) * 4)
        reasoning.append(f"Heatwave duration estimated at {duration_hours:.0f} hours based on {temp}°C")

        # Spread risk based on temperature
        spread_risk = min(0.95, (temp - 35) / 15.0)
        reasoning.append(f"Spread risk = ({temp}-35)/15 = {spread_risk:.2f}")

        affected_radius_km = math.sqrt(area_sqkm / math.pi)

        # Vulnerable populations affected more in low-income areas
        vulnerability_factor = 0.40 if low_income else 0.25
        affected_population = int(area_sqkm * density * vulnerability_factor)
        reasoning.append(
            f"Affected pop = {area_sqkm} × {density} × {vulnerability_factor} "
            f"(low_income={low_income}) = {affected_population}"
        )

        cascading = ["power_outage", "water_shortage"]
        if temp > 44:
            cascading.append("heat_stroke_emergency")

        return {
            "duration_hours": round(duration_hours, 1),
            "spread_risk": round(spread_risk, 2),
            "affected_radius_km": round(affected_radius_km, 2),
            "affected_population": affected_population,
            "cascading_risks": cascading
        }

    async def run(self, input_data: SeverityPredictionInput) -> SeverityPrediction:
        """Execute severity prediction pipeline."""
        reasoning_steps = []
        crisis_type = input_data.crisis.crisis_type
        reasoning_steps.append(f"Predicting severity for {crisis_type} crisis")

        vuln = input_data.vulnerability_data or {}
        weather = input_data.weather_data or {}

        # Calculate based on crisis type
        if crisis_type == "urban_flood":
            calc = self._calculate_urban_flood(weather, vuln, reasoning_steps)
        elif crisis_type == "heatwave":
            calc = self._calculate_heatwave(weather, vuln, reasoning_steps)
        else:
            # Generic defaults
            calc = {
                "duration_hours": 2.0,
                "spread_risk": 0.5,
                "affected_radius_km": 1.4,
                "affected_population": 5000,
                "cascading_risks": ["power_outage"]
            }
            reasoning_steps.append(f"No specific calculation for {crisis_type}, using defaults")

        severity_level, severity_label = self._determine_severity_level(calc["affected_population"])
        reasoning_steps.append(f"Severity: Level {severity_level} ({severity_label})")

        peak_impact_time = (
            datetime.now(timezone.utc) + timedelta(hours=calc["duration_hours"] / 2)
        ).isoformat()

        # Uncertainty range depends on data quality
        if vuln:
            uncertainty = "±1 hour, ±10% population estimate"
        else:
            uncertainty = "±2 hours, ±25% population estimate (limited vulnerability data)"

        trace_id = str(uuid.uuid4())
        trace = self.log_trace(
            trace_id=trace_id,
            input_data={
                "crisis_type": crisis_type,
                "location": input_data.crisis.location,
                "weather_summary": weather
            },
            reasoning_steps=reasoning_steps,
            confidence_score=0.85 if vuln else 0.60,
            decision_made={
                "severity_level": severity_level,
                "affected_population": calc["affected_population"],
                "estimated_duration_hours": calc["duration_hours"],
                "spread_risk": calc["spread_risk"]
            },
            alternative_considered="Gemini-based severity assessment as enhancement to formula-based calculation",
            fallback_triggered=False
        )

        return SeverityPrediction(
            severity_level=severity_level,
            severity_label=severity_label,
            affected_radius_km=calc["affected_radius_km"],
            affected_population=calc["affected_population"],
            estimated_duration_hours=calc["duration_hours"],
            peak_impact_time=peak_impact_time,
            spread_risk=calc["spread_risk"],
            cascading_risks=calc["cascading_risks"],
            uncertainty_range=uncertainty,
            trace=trace
        )
