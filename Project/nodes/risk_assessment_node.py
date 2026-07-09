
"""Risk assessment node.

Runs a RiskAssessmentAgent if available; otherwise uses a simple rule-based
estimator to determine a prospect's risk profile.
"""

from typing import Optional
from state import WorkflowState, RiskAssessmentResult
from config import get_logger

logger = get_logger("node.risk_assessment")


def _estimate_risk_from_data(state: WorkflowState) -> RiskAssessmentResult:
    """Simple rule-based estimator using age, horizon and savings."""
    p = state.prospect.prospect_data
    score = 0.5
    factors = []
    recommendations = []

    if p:
        # younger and long horizon -> higher risk tolerance
        if p.investment_horizon_years and p.investment_horizon_years >= 10:
            score += 0.2
            factors.append("Long investment horizon")
        else:
            factors.append("Shorter horizon")

        # income and savings
        try:
            if p.annual_income and p.annual_income > 100000:
                score += 0.1
            if p.current_savings and p.current_savings > 50000:
                score += 0.1
        except Exception:
            pass

        # experience
        if p.investment_experience_level and p.investment_experience_level.lower() in ("intermediate", "advanced"):
            score += 0.1
            factors.append("Experienced investor")
        else:
            factors.append("Limited experience")

    # clamp
    prob = max(0.0, min(1.0, score))
    # map to categorical
    if prob >= 0.7:
        level = "High"
    elif prob >= 0.4:
        level = "Moderate"
    else:
        level = "Low"

    if level == "High":
        recommendations.append("Consider growth-oriented allocations; accept higher volatility for long-term gains")
    elif level == "Moderate":
        recommendations.append("Balanced allocation with a mix of growth and defensive instruments")
    else:
        recommendations.append("Conservative allocation focusing on capital preservation")

    return RiskAssessmentResult(risk_level=level, confidence_score=prob, risk_factors=factors, recommendations=recommendations)


async def risk_assessment_node(state: WorkflowState) -> WorkflowState:
    logger.info("Starting risk_assessment node")
    state.current_step = "risk_assessment"

    try:
        # Prefer a domain agent if available
        try:
            from langraph_agents.agents.risk_assessment_agent import RiskAssessmentAgent
        except Exception:
            RiskAssessmentAgent = None

        if RiskAssessmentAgent:
            agent = RiskAssessmentAgent()
            state = await agent.execute(state)
            if state.analysis and state.analysis.risk_assessment:
                logger.info("RiskAssessmentAgent completed with level %s", state.analysis.risk_assessment.risk_level)
                if "risk_assessment" not in state.completed_steps:
                    state.completed_steps.append("risk_assessment")
                return state

        # Fallback estimator
        ra = _estimate_risk_from_data(state)
        state.analysis.risk_assessment = ra
        if "risk_assessment" not in state.completed_steps:
            state.completed_steps.append("risk_assessment")
        logger.info("Risk estimator completed: %s (%.2f)", ra.risk_level, ra.confidence_score)
        return state

    except Exception as exc:
        logger.exception("Risk assessment node failed: %s", exc)
        if "risk_assessment" not in state.failed_steps:
            state.failed_steps.append("risk_assessment")
        raise

