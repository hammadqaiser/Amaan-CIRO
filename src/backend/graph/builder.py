"""
Graph Builder — Compiles the CIRO LangGraph StateGraph.

Mirrors SlashAgents' graph/setup.py pattern.
Wires all nodes and conditional edges into a compiled graph.
"""

import logging
from langgraph.graph import StateGraph, START, END

from graph.state import CrisisState
from graph.nodes import (
    signal_ingestion_node,
    classification_node,
    severity_node,
    allocation_node,
    simulation_node,
    comms_node,
    verification_node,
)
from graph.edges import CIROEdges

logger = logging.getLogger(__name__)


class CIROGraphBuilder:
    """Builds and compiles the CIRO crisis StateGraph."""

    def __init__(self, edges: CIROEdges = None):
        self.edges = edges or CIROEdges()

    def build(self):
        """
        Build and compile the full crisis pipeline graph.

        Graph topology:
            START → Ingestion → [empty check] → Classification
                → [confidence check] → Verification ⇄ Classification (reflection, max 2)
                                     → Severity → Allocation → Simulation → Comms → END
                                     → END (monitoring/idle)
            Verification → END (retracted)
        """
        workflow = StateGraph(CrisisState)

        # ── Add all nodes ──
        workflow.add_node("signal_ingestion_node", signal_ingestion_node)
        workflow.add_node("classification_node", classification_node)
        workflow.add_node("verification_node", verification_node)
        workflow.add_node("severity_prediction_node", severity_node)
        workflow.add_node("resource_allocation_node", allocation_node)
        workflow.add_node("simulation_node", simulation_node)
        workflow.add_node("stakeholder_comms_node", comms_node)

        # ── Entry edge ──
        workflow.add_edge(START, "signal_ingestion_node")

        # ── After Ingestion: check if signals exist ──
        workflow.add_conditional_edges(
            "signal_ingestion_node",
            self.edges.route_after_ingestion,
            {
                "classification_node": "classification_node",
                "end_idle": END,
            }
        )

        # ── After Classification: confidence check ──
        workflow.add_conditional_edges(
            "classification_node",
            self.edges.route_after_classification,
            {
                "verification_node": "verification_node",
                "severity_prediction_node": "severity_prediction_node",
                "end_monitoring": END,
            }
        )

        # ── After Verification: reflect back or continue ──
        workflow.add_conditional_edges(
            "verification_node",
            self.edges.route_after_verification,
            {
                "classification_node": "classification_node",   # REFLECTION LOOP
                "severity_prediction_node": "severity_prediction_node",
                "end_retracted": END,
            }
        )

        # ── Linear pipeline continuation ──
        workflow.add_edge("severity_prediction_node", "resource_allocation_node")
        workflow.add_edge("resource_allocation_node", "simulation_node")
        workflow.add_edge("simulation_node", "stakeholder_comms_node")
        workflow.add_edge("stakeholder_comms_node", END)

        logger.info("[Builder] CIRO graph compiled successfully")
        return workflow.compile()
