# TODO: Import necessary modules and agents
# TODO: Create async persona_node function accepting WorkflowState
# TODO: Instantiate PersonaAgent
# TODO: Try to execute agent with error handling
# TODO: Log node execution with timestamps
# TODO: Update state.current_step to "persona_classification"
# TODO: Add step to completed_steps on success or failed_steps on failure
# TODO: Return state without raising (optional node - continue even if fails)
from datetime import datetime
import asyncio
from state import WorkflowState
from langraph_agents.agents import PersonaAgent
from config import get_logger


logger = get_logger("node.persona")


async def persona_node(state: WorkflowState) -> WorkflowState:
	"""Run persona classification node and update workflow state.

	This node is optional — failures should not stop the workflow.
	"""
	node_name = "persona_classification"
	state.current_step = node_name
	start = datetime.now()
	logger.info(f"Starting node {node_name} at {start.isoformat()}")

	agent = PersonaAgent()

	try:
		# Run agent — it's optional so we swallow exceptions
		await agent.run(state)
		state.completed_steps.append(node_name)
		logger.info(f"Node {node_name} completed successfully")
	except Exception as e:
		state.failed_steps.append(node_name)
		logger.warning(f"Node {node_name} failed: {e}")
	finally:
		end = datetime.now()
		duration = (end - start).total_seconds()
		logger.info(f"Node {node_name} finished in {duration:.2f}s")
		state.updated_at = datetime.now()

	return state
