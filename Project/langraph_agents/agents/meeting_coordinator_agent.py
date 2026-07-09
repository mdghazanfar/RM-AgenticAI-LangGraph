# TODO: Create MeetingCoordinatorAgent class inheriting from BaseAgent
# TODO: Implement generate_agenda creating meeting agenda items
# TODO: Implement generate_talking_points from analysis results
# TODO: Implement generate_questions creating relevant questions for prospect
# TODO: Implement generate_objection_handling creating responses to common objections
# TODO: Implement generate_next_steps creating follow-up action items
# TODO: Implement async run method:
#   - Review all analysis results (risk, persona, products, recommendations)
#   - Generate meeting agenda
#   - Create talking points highlighting key findings
#   - Generate questions to ask prospect
#   - Create objection handling strategies
#   - Generate next steps for follow-up
#   - Return MeetingGuide in state

"""Meeting coordinator agent.

Creates a meeting guide (agenda, talking points, questions, objection
handling and next steps) from the analysis and recommendation state so the
RM can run a client meeting efficiently.
"""

from typing import List, Dict, Any
from langraph_agents.base_agent import OptionalAgent
from state import WorkflowState, MeetingGuide
from config import get_logger
from langraph_agents.tools.calculation_tool import (
    generate_meeting_agenda,
    generate_meeting_talking_points,
    generate_meeting_questions,
    generate_meeting_objection_handling,
    generate_meeting_next_steps,
)

logger = get_logger("agent.meeting_coordinator")


class MeetingCoordinatorAgent(OptionalAgent):
	"""Prepare meeting materials from workflow results."""

	def __init__(self, **kwargs):
		super().__init__(name="MeetingCoordinatorAgent", description="Prepare meeting guide and materials", **kwargs)
		self.logger = logger

	async def execute(self, state: WorkflowState) -> WorkflowState:
		self.logger.info("Preparing meeting guide")

		guide = MeetingGuide(
			agenda_items=generate_meeting_agenda(state),
			key_talking_points=generate_meeting_talking_points(state),
			questions_to_ask=generate_meeting_questions(state),
			objection_handling=generate_meeting_objection_handling(state),
			next_steps=generate_meeting_next_steps(state),
			estimated_duration="45 minutes"
		)

		state.meeting.meeting_guide = guide
		state.key_insights.append("Meeting guide prepared")
		self.logger.info("Meeting guide created")
		return state


