# TODO: Import ProspectAnalysisWorkflow from graph module
# TODO: Re-export ProspectAnalysisWorkflow for convenience imports
# TODO: Add __all__ with ProspectAnalysisWorkflow
"""Lightweight workflow orchestration for prospect analysis.

This is a minimal class that orchestrates agent execution sequentially.
Replace with the graph-based orchestration when ready.
"""

from typing import List
from state import WorkflowState


class ProspectAnalysisWorkflow:
	"""Simple orchestration that runs a list of agents sequentially."""

	def __init__(self, agents: List):
		self.agents = agents

	async def run(self, state: WorkflowState) -> WorkflowState:
		for agent in self.agents:
			# Each agent follows BaseAgent interface and exposes run(state)
			state.add_agent_execution(agent.name)
			try:
				await agent.run(state)
				state.complete_agent_execution(agent.name, success=True)
			except Exception as e:
				state.complete_agent_execution(agent.name, success=False, error=str(e))
				# Continue or break depending on agent type; for simplicity continue
		return state


__all__ = ["ProspectAnalysisWorkflow"]
