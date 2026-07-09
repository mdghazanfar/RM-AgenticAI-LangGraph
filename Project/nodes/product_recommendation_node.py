
"""Product recommendation node.

Attempts to use a ProductSpecialistAgent when available; otherwise falls
back to a simple rule-based product scorer reading `data/input_data/products.csv`.
"""

from typing import List
import csv
from pathlib import Path
from state import WorkflowState, ProductRecommendation
from config import get_logger

logger = get_logger("node.product_recommendation")


def _score_product(row: dict, state: WorkflowState) -> float:
    """Simple heuristic to score a product for the prospect.

    Scores by risk alignment, fee attractiveness, and match to prospect goal.
    """
    score = 0.0
    # risk alignment
    if state.analysis and state.analysis.risk_assessment:
        try:
            ra = state.analysis.risk_assessment.risk_level.lower()
            if ra in row.get("risk_profile", "").lower():
                score += 0.5
        except Exception:
            pass

    # lower fees preferred
    try:
        fees = float(row.get("fees", "0").replace("%", ""))
        score += max(0, 0.3 - fees / 100)
    except Exception:
        score += 0.1

    # match by product type to goal
    goal = (state.prospect.prospect_data.investment_goal or "").lower() if state.prospect.prospect_data else ""
    if goal and goal in row.get("product_name", "").lower():
        score += 0.3

    return score


async def product_recommendation_node(state: WorkflowState) -> WorkflowState:
    logger.info("Starting product_recommendation node")
    state.current_step = "product_recommendation"

    # prefer using a domain agent if available
    try:
        from langraph_agents.agents.product_specialist_agent import ProductSpecialistAgent
    except Exception:
        ProductSpecialistAgent = None

    try:
        if ProductSpecialistAgent:
            agent = ProductSpecialistAgent()
            state = await agent.execute(state)
            if state.recommendations and state.recommendations.recommended_products:
                logger.info("ProductSpecialistAgent provided %d recommendations", len(state.recommendations.recommended_products))
                if "product_recommendation" not in state.completed_steps:
                    state.completed_steps.append("product_recommendation")
                return state

        # Fallback: read products.csv and run a heuristic
        products_path = Path(__file__).resolve().parents[2] / "data" / "input_data" / "products.csv"
        recommendations: List[ProductRecommendation] = []
        if products_path.exists():
            with products_path.open("r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                scored = []
                for r in reader:
                    s = _score_product(r, state)
                    scored.append((s, r))

                scored.sort(key=lambda x: x[0], reverse=True)
                for score, row in scored[:5]:
                    pr = ProductRecommendation(
                        product_id=row.get("product_id") or row.get("id") or "",
                        product_name=row.get("product_name") or row.get("name") or "",
                        product_type=row.get("product_type") or row.get("type") or "",
                        suitability_score=min(max(score, 0.0), 1.0),
                        justification=f"Heuristic match score {score:.2f}",
                        risk_alignment=row.get("risk_profile", ""),
                        expected_returns=row.get("expected_returns", ""),
                        fees=row.get("fees", "N/A"),
                    )
                    recommendations.append(pr)

        state.recommendations.recommended_products = recommendations
        if "product_recommendation" not in state.completed_steps:
            state.completed_steps.append("product_recommendation")
        logger.info("Product recommendation node completed with %d recommendations", len(recommendations))
        return state

    except Exception as exc:
        logger.exception("Product recommendation node failed: %s", exc)
        if "product_recommendation" not in state.failed_steps:
            state.failed_steps.append("product_recommendation")
        raise
