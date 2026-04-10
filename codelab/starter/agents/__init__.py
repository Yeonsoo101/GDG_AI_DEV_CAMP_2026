# Package marker — do not add imports here.
# Eager imports trigger a circular load:
#   orchestrator_agent.agent → agents → agents.orchestrator_agent.agent (second load)
# deploy.py imports root_agent directly from agents.orchestrator_agent.agent.
