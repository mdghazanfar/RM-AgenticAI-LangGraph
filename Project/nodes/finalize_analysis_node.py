# TODO: Create async finalize_analysis_node function accepting WorkflowState
# TODO: Collect confidence scores from all analysis results
# TODO: Calculate overall_confidence as average of available scores
# TODO: Generate key_insights list from:
#   - Risk assessment findings
#   - Persona classification
#   - Top product recommendations
#   - Data quality assessment
# TODO: Generate action_items list from:
#   - Data validation issues
#   - Risk-specific actions
#   - Product presentation actions
#   - Persona-specific talking points
#   - Follow-up meeting scheduling
# TODO: Update state timestamps and completion status
# TODO: Add "finalize_analysis" to completed_steps
# TODO: Log completion with metrics
# TODO: Return final state


"""Finalize analysis node: summarize findings and prepare final actions."""

from typing import List
from state import WorkflowState
from config import get_logger

logger = get_logger("node.finalize")


async def finalize_analysis_node(state: WorkflowState) -> WorkflowState:
	"""Aggregate analysis results into final insights and actions.

	This node is idempotent and should be safe to run multiple times.
	"""
	logger.info("Running finalize_analysis_node")

	scores: List[float] = []
	if state.analysis and state.analysis.risk_assessment and state.analysis.risk_assessment.confidence_score is not None:
		scores.append(state.analysis.risk_assessment.confidence_score)
	if state.analysis and state.analysis.persona_classification and state.analysis.persona_classification.confidence_score is not None:
		scores.append(state.analysis.persona_classification.confidence_score)
	if state.analysis and state.analysis.goal_prediction and state.analysis.goal_prediction.probability is not None:
		scores.append(state.analysis.goal_prediction.probability)

	overall = sum(scores) / len(scores) if scores else 0.0
	state.overall_confidence = overall

	insights: List[str] = []
	if state.analysis.risk_assessment:
		ra = state.analysis.risk_assessment
		insights.append(f"Risk profile: {ra.risk_level} (confidence {ra.confidence_score:.2f})")
		if ra.recommendations:
			insights.extend([f"Risk action: {r}" for r in ra.recommendations[:3]])

	if state.analysis.persona_classification:
		p = state.analysis.persona_classification
		insights.append(f"Persona: {p.persona_type} (confidence {p.confidence_score:.2f})")

	if state.recommendations and state.recommendations.recommended_products:
		top = state.recommendations.recommended_products[:3]
		insights.append("Top product picks: " + ", ".join([f"{t.product_name} ({t.suitability_score:.2f})" for t in top]))

	# Data quality
	if state.prospect and state.prospect.validation_errors:
		insights.append("Data validation issues found: " + ", ".join(state.prospect.validation_errors[:3]))

	state.key_insights = insights

	actions: List[str] = []
	# Data fixes
	if state.prospect and state.prospect.missing_fields:
		actions.append("Request missing fields: " + ", ".join(state.prospect.missing_fields))

	# Risk actions
	if state.analysis and state.analysis.risk_assessment and state.analysis.risk_assessment.recommendations:
		actions.extend(state.analysis.risk_assessment.recommendations[:3])

	# Presentations
	if state.recommendations and state.recommendations.recommended_products:
		actions.append("Prepare product factsheets and suitability notes for top recommendations")

	# Persona-specific talking points
	if state.analysis and state.analysis.persona_classification:
		actions.append(f"Tailor meeting language for persona: {state.analysis.persona_classification.persona_type}")

	# Follow-up scheduling
	actions.append("Schedule follow-up meeting in 30 days to review progress")

	state.action_items = actions

	# Mark finalize step done
	if "finalize_analysis" not in state.completed_steps:
		state.completed_steps.append("finalize_analysis")

	state.updated_at = __import__("datetime").datetime.utcnow()

	logger.info("Finalize complete: overall_confidence=%.2f, insights=%d, actions=%d", overall, len(insights), len(actions))
	return state


