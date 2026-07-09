# TODO: Create PortfolioOptimizerAgent class inheriting from BaseAgent
# TODO: Implement optimize_allocation creating balanced portfolio
# TODO: Implement apply_risk_constraints limiting allocation based on risk
# TODO: Implement calculate_diversification metrics
# TODO: Implement validate_allocation checking portfolio constraints
# TODO: Implement async run method:
#   - Get risk assessment and recommended products
#   - Create initial allocation based on modern portfolio theory
#   - Apply risk-based constraints
#   - Optimize for diversification
#   - Validate allocation meets requirements
#   - Return portfolio_allocation dict in state

"""Portfolio optimizer agent.

Provides a lightweight, deterministic portfolio allocation that integrates
recommended products and the prospect's risk assessment. This is intentionally
simple and heuristic-driven so it can run without heavy dependencies.
"""

from typing import List, Dict, Any, Optional, Tuple
from config import get_logger, get_settings
from langraph_agents.base_agent import OptionalAgent
from state import WorkflowState, ProductRecommendation, ProspectData
from langraph_agents.tools.calculation_tool import (
    calculate_portfolio_weights,
    apply_portfolio_risk_constraints,
    calculate_portfolio_diversification,
    validate_portfolio_allocation,
)


class PortfolioOptimizerAgent(OptionalAgent):
	"""Create a portfolio allocation from recommended products and risk profile."""

	def __init__(self, **kwargs):
		settings = get_settings()
		llm = None
		super().__init__(name="PortfolioOptimizerAgent", description="Optimize product allocations", llm=llm, **kwargs)
		self.logger = get_logger("agent.PortfolioOptimizerAgent")

	async def execute(self, state: WorkflowState) -> WorkflowState:
		"""Main execution entry point.

		Steps:
		- Collect recommended products from state, or create fallback buckets.
		- Compute initial weights, apply risk constraints, validate and store.
		"""
		self.logger.info("Starting portfolio optimization")

		products = state.recommendations.recommended_products

		# Fallback: simple generic buckets if no product recommendations provided
		if not products:
			self.logger.info("No recommended products found; creating fallback buckets")
			products = [
				ProductRecommendation(product_id="equity_bucket", product_name="Equity Basket", product_type="Equity", suitability_score=0.5, justification="Fallback equity", risk_alignment="High", expected_returns="8-12%", fees="0.5%"),
				ProductRecommendation(product_id="debt_bucket", product_name="Debt Basket", product_type="Debt", suitability_score=0.3, justification="Fallback debt", risk_alignment="Low", expected_returns="4-6%", fees="0.2%"),
				ProductRecommendation(product_id="hybrid_bucket", product_name="Hybrid Basket", product_type="Hybrid", suitability_score=0.2, justification="Fallback hybrid", risk_alignment="Moderate", expected_returns="5-8%", fees="0.3%"),
			]

		# Determine risk level from analysis (default Moderate)
		risk_level = "Moderate"
		if state.analysis and state.analysis.risk_assessment and state.analysis.risk_assessment.risk_level:
			risk_level = state.analysis.risk_assessment.risk_level

		# Build initial allocation based on suitability
		base_alloc = calculate_portfolio_weights(products)

		# Adjust for risk
		adjusted_alloc = apply_portfolio_risk_constraints(base_alloc, products, risk_level)

		# Validate and finalize
		final_alloc = validate_portfolio_allocation(adjusted_alloc)

		# Store as percentages (0.0-1.0) in state
		state.recommendations.portfolio_allocation = final_alloc

		# Add insights
		div_metrics = calculate_portfolio_diversification(final_alloc, products)
		insight = f"Portfolio optimized into {div_metrics['num_products']} products; max allocation {div_metrics['max_allocation']:.2%}; diversification score {div_metrics['diversification_score']:.2f}"
		state.key_insights.append(insight)

		self.logger.info("Portfolio optimization complete")
		return state


