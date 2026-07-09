# TODO: Create GoalPlanningAgent class inheriting from BaseAgent
# TODO: Import predict_goal_success from ml.training
# TODO: Implement analyze_goal_feasibility assessing if goals are achievable
# TODO: Implement calculate_success_probability based on financial metrics
# TODO: Implement identify_success_factors listing favorable conditions
# TODO: Implement identify_challenges listing obstacles
# TODO: Implement analyze_timeline assessing goal timeline
# TODO: Implement async run method:
#   - Extract investment goal and timeline from prospect
#   - Call ML model via predict_goal_success
#   - Perform AI-based feasibility analysis
#   - Identify success factors and challenges
#   - Analyze timeline
#   - Return GoalPredictionResult in state

"""Goal planning agent.

Performs feasibility analysis for a prospect's financial goal. Tries to use
an ML model (`predict_goal_success`) if available and falls back to simple
rule-based heuristics otherwise.
"""

from langraph_agents.base_agent import OptionalAgent
from state import WorkflowState, ProspectData, GoalPredictionResult
from config import get_logger, get_settings
from pathlib import Path
import joblib
from typing import Dict, Any, Optional
from langraph_agents.tools.ml_prediction_tool import predict_goal_success_tool
from langraph_agents.tools.calculation_tool import (
    calculate_heuristic_success_probability,
    identify_success_factors,
    identify_challenges,
    analyze_goal_timeline
)


class GoalPlanningAgent(OptionalAgent):
	"""Analyze whether a prospect's financial goal is achievable."""

	def __init__(self, **kwargs):
		settings = get_settings()
		super().__init__(name="GoalPlanningAgent", description="Assess goal feasibility and timeline", **kwargs)
		self.logger = get_logger("agent.GoalPlanningAgent")

		# Attempt to load optional ML model and encoders so tests and callers can
		# check for attributes like `goal_model` and `goal_encoders`.
		self.goal_model, self.goal_encoders = self._load_models()

	def _load_models(self) -> tuple[Optional[Any], Optional[Dict[str, Any]]]:
		"""Load optional goal prediction model and encoders from configured paths.
		Returns (model, encoders) or (None, None) on failure.
		"""
		settings = get_settings()
		try:
			model_path = Path(settings.goal_model_path)
			encoders_path = Path(settings.goal_encoders_path)
			model = joblib.load(model_path) if model_path.exists() else None
			encoders = joblib.load(encoders_path) if encoders_path.exists() else None
			self.logger.info("Goal ML models loaded successfully")
			return model, encoders
		except Exception as e:
			self.logger.warning(f"Could not load goal ML models: {e}")
			return None, None

	async def execute(self, state: WorkflowState) -> WorkflowState:
		"""Main execution. Populates state.analysis.goal_prediction."""
		self.logger.info("GoalPlanningAgent: starting goal feasibility analysis")

		prospect = state.prospect.prospect_data
		if not prospect:
			self.logger.warning("No prospect data available for goal planning")
			return state

		# Try ML model if available
		model_result = None
		try:
			maybe = predict_goal_success_tool({
				"investment_goal": prospect.investment_goal or "",
				"age": prospect.age,
				"annual_income": prospect.annual_income,
				"current_savings": prospect.current_savings,
				"target_goal_amount": prospect.target_goal_amount,
				"investment_horizon_years": prospect.investment_horizon_years,
				"number_of_dependents": prospect.number_of_dependents,
				"investment_experience_level": prospect.investment_experience_level,
			})
			model_result = await maybe
		except Exception as e:
			self.logger.warning(f"predict_goal_success_tool failed: {e}")
			model_result = None

		# Determine probability and labels
		if model_result and isinstance(model_result, dict) and "probability" in model_result and model_result.get("goal_success") != "Unknown":
			probability = float(model_result.get("probability", 0.5))
			goal_success = model_result.get("goal_success", "Likely" if probability >= 0.5 else "Unlikely")
		else:
			probability = calculate_heuristic_success_probability(prospect)
			goal_success = "Likely" if probability >= 0.5 else "Unlikely"

		success_factors = identify_success_factors(prospect)
		challenges = identify_challenges(prospect)
		timeline = analyze_goal_timeline(prospect, probability)

		result = GoalPredictionResult(
			goal_success=goal_success,
			probability=round(probability, 3),
			success_factors=success_factors,
			challenges=challenges,
			timeline_analysis=timeline,
		)

		state.analysis.goal_prediction = result
		self.logger.info(f"Goal planning complete: {goal_success} (p={probability:.2f})")

		return state


