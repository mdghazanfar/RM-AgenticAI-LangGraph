# TODO: Create ComplianceAgent class inheriting from BaseAgent
# TODO: Implement check_suitability_compliance verifying product matches investor profile
# TODO: Implement check_regulatory_compliance validating against regulations
# TODO: Implement generate_required_disclosures creating disclosure list
# TODO: Implement identify_potential_violations finding compliance issues
# TODO: Implement async run method:
#   - Review recommendations and prospect profile
#   - Check suitability of recommended products
#   - Verify regulatory compliance
#   - Generate required disclosures
#   - Identify any violations or warnings
#   - Calculate compliance score
#   - Return ComplianceCheck in state

"""Compliance agent.

Performs lightweight suitability and regulatory checks on recommended products
for a prospect. This implementation purposely avoids external regulatory
databases and instead uses heuristic rules suitable for unit testing and as a
starting point for integration with a real compliance engine.
"""

from typing import List, Dict, Any, Optional
from config import get_settings, get_logger
from langraph_agents.base_agent import CriticalAgent
from state import WorkflowState, ProductRecommendation, ProspectData, ComplianceCheck
from langraph_agents.tools.calculation_tool import (
    check_suitability_compliance,
    check_regulatory_compliance,
    generate_required_disclosures,
    identify_potential_violations,
)


class ComplianceAgent(CriticalAgent):
	"""Validate product recommendations against prospect profile and basic rules."""

	def __init__(self, **kwargs):
		settings = get_settings()
		super().__init__(name="ComplianceAgent", description="Perform suitability and regulatory checks", **kwargs)
		self.logger = get_logger("agent.ComplianceAgent")

	async def execute(self, state: WorkflowState) -> WorkflowState:
		"""Run compliance checks and store a ComplianceCheck in the workflow state."""
		self.logger.info("ComplianceAgent: starting compliance checks")

		prospect = state.prospect.prospect_data
		products = state.recommendations.recommended_products or []

		suitability = check_suitability_compliance(prospect, products)
		regulatory = check_regulatory_compliance(products)

		combined = identify_potential_violations(suitability, regulatory)

		disclosures = generate_required_disclosures(products)

		# Compute a simple compliance score: 1.0 - penalty for violations and warnings
		num_violations = len(combined.get("violations", []))
		num_warnings = len(combined.get("warnings", []))
		score = max(0.0, 1.0 - (0.5 * num_violations + 0.1 * num_warnings))

		compliance = ComplianceCheck(
			is_compliant=(num_violations == 0),
			compliance_score=round(score, 3),
			violations=combined.get("violations", []),
			warnings=combined.get("warnings", []),
			required_disclosures=disclosures,
		)

		state.recommendations.compliance_check = compliance

		self.logger.info(f"Compliance check complete: compliant={compliance.is_compliant}, score={compliance.compliance_score}")

		return state



