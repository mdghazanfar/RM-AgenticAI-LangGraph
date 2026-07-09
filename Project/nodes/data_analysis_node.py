# TODO: Import necessary modules and agents
# TODO: Create async data_analysis_node function accepting WorkflowState
# TODO: Instantiate DataAnalystAgent
# TODO: Call agent.execute(state) with error handling
# TODO: Log node execution with timestamps
# TODO: Update state.current_step to "data_analysis"
# TODO: Add step to completed_steps on success or failed_steps on failure
# TODO: Return updated state
from datetime import datetime
import asyncio
from state import WorkflowState
from langraph_agents.agents import DataAnalystAgent
from config import get_logger

logger = get_logger("node.data_analysis")


async def data_analysis_node(state: WorkflowState) -> WorkflowState:
	"""Run the DataAnalystAgent and update WorkflowState.

	This node is critical; failures will raise so the workflow can stop.
	"""
	node_name = "data_analysis"
	state.current_step = node_name
	start = datetime.now()
	logger.info(f"Starting node {node_name} at {start.isoformat()}")

	agent = DataAnalystAgent()
	try:
		# Agents expose run(...) which is async
		await agent.run(state)
		state.completed_steps.append(node_name)
		logger.info(f"Node {node_name} completed successfully")
	except Exception as e:
		state.failed_steps.append(node_name)
		logger.exception(f"Node {node_name} failed: {e}")
		raise
	finally:
		end = datetime.now()
		duration = (end - start).total_seconds()
		logger.info(f"Node {node_name} finished in {duration:.2f}s")
		state.updated_at = datetime.now()

	return state

