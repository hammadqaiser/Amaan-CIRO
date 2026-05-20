import sys
import os

print("--- CONFTEST LOADED (ORDERED ALIASING) ---")

# Ensure the root of the project is in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 1. Alias models.schemas first before any agent imports it!
import src.backend.models.schemas as schemas
sys.modules['models.schemas'] = schemas
sys.modules['models'] = sys.modules['src.backend.models']

# 2. Alias base_agent
import src.backend.agents.base_agent as base_agent
sys.modules['agents.base_agent'] = base_agent

# 3. Alias signal_ingestion
import src.backend.agents.signal_ingestion as signal_ingestion
sys.modules['agents.signal_ingestion'] = signal_ingestion

# 4. Alias crisis_classification
import src.backend.agents.crisis_classification as crisis_classification
sys.modules['agents.crisis_classification'] = crisis_classification

# 5. Alias severity_prediction
import src.backend.agents.severity_prediction as severity_prediction
sys.modules['agents.severity_prediction'] = severity_prediction

# 6. Alias resource_allocation
import src.backend.agents.resource_allocation as resource_allocation
sys.modules['agents.resource_allocation'] = resource_allocation

# 7. Alias simulation
import src.backend.agents.simulation as simulation
sys.modules['agents.simulation'] = simulation

# 8. Alias stakeholder_comms
import src.backend.agents.stakeholder_comms as stakeholder_comms
sys.modules['agents.stakeholder_comms'] = stakeholder_comms

# 9. Alias verification
import src.backend.agents.verification as verification
sys.modules['agents.verification'] = verification

# 10. Alias chat_agent
import src.backend.agents.chat_agent as chat_agent
sys.modules['agents.chat_agent'] = chat_agent

# 11. Alias orchestrator
import src.backend.orchestrator as orchestrator
sys.modules['orchestrator'] = orchestrator

# Ensure sys.modules['agents'] points to the right package
sys.modules['agents'] = sys.modules['src.backend.agents']
