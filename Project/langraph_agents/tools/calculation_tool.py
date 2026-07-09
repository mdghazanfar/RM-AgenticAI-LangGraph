import math
from typing import List, Dict, Any, Optional
from math import isclose
from state import ProspectData, ProductRecommendation, WorkflowState
from config import get_logger

logger = get_logger("tools.calculation_tool")

# ----------------------------------------------------
# Goal Planning Calculations (GoalPlanningAgent)
# ----------------------------------------------------

def calculate_heuristic_success_probability(prospect: ProspectData) -> float:
    """Heuristic probability (0.0-1.0) based on savings, income, horizon and target."""
    try:
        annual_savings = max(0.0, prospect.annual_income * 0.10)
        horizon = max(1, prospect.investment_horizon_years)
        funded = prospect.current_savings + annual_savings * horizon
        ratio = funded / max(1.0, prospect.target_goal_amount)

        # Map to probability using logistic-like curve
        prob = 1.0 / (1.0 + math.exp(-4 * (ratio - 1.0)))
        # Adjust for dependents and experience
        if prospect.number_of_dependents > 2:
            prob *= 0.9
        if prospect.investment_experience_level and prospect.investment_experience_level.lower() == "beginner":
            prob *= 0.95

        return max(0.0, min(1.0, prob))
    except Exception as e:
        logger.error(f"Error calculating heuristic probability: {e}")
        return 0.5

def identify_success_factors(prospect: ProspectData) -> list:
    factors = []
    if prospect.current_savings and prospect.current_savings > 0:
        factors.append("Existing savings provide a head start")
    if prospect.investment_horizon_years >= 10:
        factors.append("Long investment horizon supports compounding")
    if prospect.investment_experience_level and prospect.investment_experience_level.lower() in ("advanced", "intermediate"):
        factors.append("Investor experience helps with disciplined investing")
    if prospect.annual_income and prospect.annual_income > 500000:
        factors.append("Higher income enables larger periodic savings")
    return factors

def identify_challenges(prospect: ProspectData) -> list:
    challenges = []
    if prospect.target_goal_amount and prospect.target_goal_amount > (prospect.annual_income * 5):
        challenges.append("Target significantly exceeds typical savings capacity; may need longer horizon or higher savings rate")
    if prospect.number_of_dependents and prospect.number_of_dependents > 2:
        challenges.append("Multiple dependents increase financial obligations")
    if prospect.investment_experience_level and prospect.investment_experience_level.lower() == "beginner":
        challenges.append("Limited experience may increase risk of suboptimal choices")
    return challenges

def analyze_goal_timeline(prospect: ProspectData, probability: float) -> Dict[str, Any]:
    """Produce a simple timeline analysis with estimated years to goal."""
    annual_savings = max(1.0, prospect.annual_income * 0.10)
    remaining = max(0.0, prospect.target_goal_amount - prospect.current_savings)
    years_needed = remaining / annual_savings
    years_needed = max(0.0, years_needed)

    return {
        "estimated_years_to_goal": round(years_needed, 1),
        "probability": round(probability, 3),
    }

# ----------------------------------------------------
# Portfolio Optimization Calculations (PortfolioOptimizerAgent)
# ----------------------------------------------------

def calculate_portfolio_weights(products: List[ProductRecommendation]) -> Dict[str, float]:
    """Create base weights proportional to suitability_score."""
    if not products:
        return {}

    scores = {}
    for p in products:
        score = float(p.suitability_score) if p.suitability_score is not None else 0.01
        scores[p.product_id] = max(score, 0.0)

    total = sum(scores.values())
    if total <= 0:
        n = len(products)
        return {p.product_id: 1.0 / n for p in products}

    return {pid: score / total for pid, score in scores.items()}

def apply_portfolio_risk_constraints(allocation: Dict[str, float], products: List[ProductRecommendation], risk_level: str) -> Dict[str, float]:
    """Modify allocation to respect stated risk level."""
    if not allocation:
        return allocation

    adjusted = allocation.copy()
    risk_map = {p.product_id: (p.risk_alignment or "Moderate") for p in products}

    for pid, w in allocation.items():
        alignment = risk_map.get(pid, "Moderate")
        if risk_level == "Low":
            if alignment.lower() == "high":
                adjusted[pid] = w * 0.25
            elif alignment.lower() == "moderate":
                adjusted[pid] = w * 0.8
        elif risk_level == "Moderate":
            if alignment.lower() == "high":
                adjusted[pid] = w * 0.6
        elif risk_level == "High":
            if alignment.lower() == "high":
                adjusted[pid] = w * 1.1

    total = sum(adjusted.values())
    if total <= 0:
        n = len(adjusted)
        return {k: 1.0 / n for k in adjusted}

    return {k: v / total for k, v in adjusted.items()}

def calculate_portfolio_diversification(allocation: Dict[str, float], products: List[ProductRecommendation]) -> Dict[str, Any]:
    """Return simple diversification metrics."""
    if not allocation:
        return {"num_products": 0, "max_allocation": 0.0, "diversification_score": 0.0}

    num_products = len(allocation)
    max_alloc = max(allocation.values())
    diversification_score = max(0.0, 1.0 - max_alloc)

    return {
        "num_products": num_products,
        "max_allocation": max_alloc,
        "diversification_score": diversification_score,
    }

def validate_portfolio_allocation(allocation: Dict[str, float]) -> Dict[str, float]:
    """Ensure allocation is valid: non-negative and sums to 1 (within tolerance)."""
    if not allocation:
        return allocation

    for v in allocation.values():
        if v < 0:
            logger.warning("Negative allocation found; rebalancing equally")
            n = len(allocation)
            return {k: 1.0 / n for k in allocation}

    total = sum(allocation.values())
    if not isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6):
        return {k: v / total for k, v in allocation.items()} if total > 0 else {k: 1.0 / len(allocation) for k in allocation}

    return allocation

# ----------------------------------------------------
# Compliance Calculations (ComplianceAgent)
# ----------------------------------------------------

def check_suitability_compliance(prospect: Optional[ProspectData], products: List[ProductRecommendation]) -> Dict[str, Any]:
    """Check whether recommended products are suitable for the prospect."""
    violations: List[str] = []
    warnings: List[str] = []
    per_product: Dict[str, Dict[str, Any]] = {}

    for p in products:
        pid = p.product_id
        per_product[pid] = {"name": p.product_name, "issues": []}

        try:
            score = float(p.suitability_score) if p.suitability_score is not None else 0.0
        except Exception:
            score = 0.0

        alignment = (p.risk_alignment or "Moderate").lower()

        if prospect and hasattr(prospect, "investment_experience_level") and prospect.investment_experience_level:
            if prospect.investment_experience_level.lower() == "beginner" and alignment == "high":
                if score < 0.6:
                    msg = f"Product {p.product_name} (high risk) may be unsuitable for beginner investor."
                    violations.append(msg)
                    per_product[pid]["issues"].append(msg)

        if alignment == "high" and score < 0.3:
            msg = f"High-risk product {p.product_name} has low suitability score ({score:.2f})."
            warnings.append(msg)
            per_product[pid]["issues"].append(msg)

        if not getattr(p, "fees", None):
            msg = f"Product {p.product_name} missing fee disclosure."
            warnings.append(msg)
            per_product[pid]["issues"].append(msg)

        if not getattr(p, "expected_returns", None):
            msg = f"Product {p.product_name} missing expected returns disclosure."
            warnings.append(msg)
            per_product[pid]["issues"].append(msg)

    return {"violations": violations, "warnings": warnings, "per_product": per_product}

def check_regulatory_compliance(products: List[ProductRecommendation]) -> Dict[str, Any]:
    """Simple regulatory checks: required disclosures and prohibited product types."""
    violations: List[str] = []
    warnings: List[str] = []

    prohibited_types = {"binary_option", "unregulated_derivative"}

    for p in products:
        ptype = (p.product_type or "").lower()
        if ptype in prohibited_types:
            msg = f"Product {p.product_name} of type {p.product_type} is prohibited by policy."
            violations.append(msg)

        if not getattr(p, "fees", None):
            warnings.append(f"Product {p.product_name} has no fee disclosure")

    return {"violations": violations, "warnings": warnings}

def generate_required_disclosures(products: List[ProductRecommendation]) -> List[str]:
    """Generate a short list of disclosures required per product if missing."""
    disclosures: List[str] = []
    for p in products:
        parts: List[str] = []
        if not getattr(p, "fees", None):
            parts.append("Fees and charges: provide full fee breakup")
        if not getattr(p, "expected_returns", None):
            parts.append("Expected returns: provide target return range and assumptions")
        if parts:
            disclosures.append(f"{p.product_name}: " + "; ".join(parts))

    return disclosures

def identify_potential_violations(suitability_checks: Dict[str, Any], regulatory_checks: Dict[str, Any]) -> Dict[str, Any]:
    """Combine the different check outputs into a unified compliance result."""
    violations = suitability_checks.get("violations", []) + regulatory_checks.get("violations", [])
    warnings = suitability_checks.get("warnings", []) + regulatory_checks.get("warnings", [])

    # Deduplicate preserving order
    seen = set()
    dedup_violations = []
    for v in violations:
        if v not in seen:
            dedup_violations.append(v)
            seen.add(v)

    seen = set()
    dedup_warnings = []
    for w in warnings:
        if w not in seen:
            dedup_warnings.append(w)
            seen.add(w)

    return {"violations": dedup_violations, "warnings": dedup_warnings}

# ----------------------------------------------------
# Risk Assessment Heuristics (RiskAssessmentAgent)
# ----------------------------------------------------

def rule_based_risk_assessment(prospect_data: ProspectData) -> Dict[str, Any]:
    """Fallback rule-based risk scoring."""
    score = 0
    
    # Age scoring
    if prospect_data.age is not None:
        if prospect_data.age < 35:
            score += 2
        elif prospect_data.age < 50:
            score += 1
    
    # Income scoring
    if prospect_data.annual_income is not None:
        if prospect_data.annual_income > 1000000:
            score += 2
        elif prospect_data.annual_income > 500000:
            score += 1
    
    # Horizon scoring
    if prospect_data.investment_horizon_years is not None:
        if prospect_data.investment_horizon_years > 10:
            score += 2
        elif prospect_data.investment_horizon_years > 5:
            score += 1
    
    # Experience scoring
    if prospect_data.investment_experience_level == "Advanced":
        score += 2
    elif prospect_data.investment_experience_level == "Intermediate":
        score += 1
    
    # Dependents (negative factor)
    if prospect_data.number_of_dependents is not None:
        if prospect_data.number_of_dependents > 2:
            score -= 1
    
    # Determine risk level
    if score >= 6:
        risk_level = "High"
        confidence = 0.75
    elif score >= 3:
        risk_level = "Moderate"
        confidence = 0.70
    else:
        risk_level = "Low"
        confidence = 0.65
    
    return {
        "risk_level": risk_level,
        "confidence": confidence
    }

def generate_rule_based_factors(prospect_data: ProspectData, ml_result: Dict) -> list:
    """Generate risk factors based on rules."""
    factors = []
    
    if prospect_data.age is not None:
        if prospect_data.age < 30:
            factors.append("Young age provides longer investment horizon for recovery")
        elif prospect_data.age > 55:
            factors.append("Approaching retirement age requires capital preservation focus")
    
    if prospect_data.annual_income is not None:
        if prospect_data.annual_income > 1000000:
            factors.append("High income provides buffer for risk tolerance")
        elif prospect_data.annual_income < 500000:
            factors.append("Limited income requires careful risk management")
    
    if prospect_data.number_of_dependents is not None:
        if prospect_data.number_of_dependents > 2:
            factors.append("Multiple dependents increase financial obligations")
    
    return factors

def generate_rule_based_recommendations(risk_level: str) -> list:
    """Generate recommendations based on risk level."""
    recommendations = {
        "Low": [
            "Focus on capital preservation strategies",
            "Consider fixed income and debt instruments",
            "Maintain emergency fund of 6-12 months expenses"
        ],
        "Moderate": [
            "Balance between growth and stability",
            "Diversify across asset classes",
            "Regular portfolio rebalancing recommended"
        ],
        "High": [
            "Can pursue aggressive growth strategies",
            "Higher equity allocation appropriate",
            "Monitor volatility and adjust as needed"
        ]
    }
    
    return recommendations.get(risk_level, recommendations["Moderate"])

# ----------------------------------------------------
# Persona Heuristics (PersonaAgent)
# ----------------------------------------------------

def rule_based_persona_classification(prospect_data: ProspectData, risk_level: Optional[str]) -> str:
    """Rule-based persona classification."""
    score = 0
    
    # Age factor
    if prospect_data.age is not None:
        if prospect_data.age < 35:
            score += 2
        elif prospect_data.age < 50:
            score += 1
    
    # Horizon factor
    if prospect_data.investment_horizon_years is not None:
        if prospect_data.investment_horizon_years > 10:
            score += 2
        elif prospect_data.investment_horizon_years > 5:
            score += 1
    
    # Experience factor
    if prospect_data.investment_experience_level == "Advanced":
        score += 2
    elif prospect_data.investment_experience_level == "Intermediate":
        score += 1
    
    # Risk level factor
    if risk_level:
        if risk_level == "High":
            score += 2
        elif risk_level == "Moderate":
            score += 1
    
    # Classify
    if score >= 6:
        return "Aggressive Growth"
    elif score >= 3:
        return "Steady Saver"
    else:
        return "Cautious Planner"

def get_persona_characteristics(persona_type: str) -> List[str]:
    """Get characteristics for persona type."""
    characteristics = {
        "Aggressive Growth": [
            "High risk tolerance with focus on capital appreciation",
            "Long-term investment horizon enabling growth strategies",
            "Comfortable with market volatility and fluctuations",
            "Seeks maximum returns through equity and growth instruments"
        ],
        "Steady Saver": [
            "Balanced approach to risk and returns",
            "Consistent savings behavior with clear financial goals",
            "Prefers diversified portfolio across asset classes",
            "Values both growth and stability in investments"
        ],
        "Cautious Planner": [
            "Conservative risk profile prioritizing capital preservation",
            "Prefers predictable and stable returns",
            "Strong focus on financial security",
            "Comfortable with lower returns for reduced risk"
        ]
    }
    
    return characteristics.get(persona_type, characteristics["Steady Saver"])

def calculate_persona_confidence_score(prospect_data: ProspectData, persona_type: str) -> float:
    """Calculate classification confidence."""
    confidence = 0.7  # Base confidence
    
    # Age alignment
    if prospect_data.age is not None:
        if persona_type == "Aggressive Growth" and prospect_data.age < 40:
            confidence += 0.1
        elif persona_type == "Cautious Planner" and prospect_data.age > 50:
            confidence += 0.1
    
    # Horizon alignment
    if prospect_data.investment_horizon_years is not None:
        if persona_type == "Aggressive Growth" and prospect_data.investment_horizon_years > 10:
            confidence += 0.1
        elif persona_type == "Cautious Planner" and prospect_data.investment_horizon_years < 5:
            confidence += 0.1
    
    # Experience alignment
    if prospect_data.investment_experience_level == "Advanced":
        confidence += 0.05
    
    return min(0.95, confidence)

def get_default_behavioral_insights(persona_type: str) -> List[str]:
    """Default behavioral insights."""
    default_insights = {
        "Aggressive Growth": [
            "Likely to embrace new investment opportunities",
            "May need guidance on diversification strategies",
            "Values growth potential over short-term stability"
        ],
        "Steady Saver": [
            "Demonstrates disciplined financial planning",
            "Open to learning about investment strategies",
            "Seeks balance between risk and reward"
        ],
        "Cautious Planner": [
            "Values transparency and clear explanations",
            "Requires reassurance about investment safety",
            "Prefers proven and established investment vehicles"
        ]
    }
    
    return default_insights.get(persona_type, default_insights["Steady Saver"])

# ----------------------------------------------------
# Meeting Coordinator Heuristics (MeetingCoordinatorAgent)
# ----------------------------------------------------

def generate_meeting_agenda(state: WorkflowState) -> List[str]:
    """Generate meeting agenda items."""
    agenda = [
        "Introductions and meeting purpose",
        "Review prospect's financial objectives",
        "Discuss risk profile and recommended approach",
        "Present recommended products and portfolio allocation",
        "Address questions & objections",
        "Agree next steps and timelines"
    ]

    # If a goal prediction exists, add a dedicated agenda item
    if state.analysis and state.analysis.goal_prediction:
        agenda.insert(3, "Discuss goal feasibility and timeline")

    return agenda

def generate_meeting_talking_points(state: WorkflowState) -> List[str]:
    """Generate talking points based on analysis results."""
    points = []

    prospect = state.prospect.prospect_data if state.prospect else None
    if prospect:
        points.append(f"Prospect: {prospect.name}, Age: {prospect.age}, Income: {prospect.annual_income}")

    if state.analysis and state.analysis.risk_assessment:
        ra = state.analysis.risk_assessment
        points.append(f"Risk profile: {ra.risk_level} (confidence {ra.confidence_score:.2f})")
        if ra.risk_factors:
            points.append("Key risk factors: " + ", ".join(ra.risk_factors[:3]))

    if state.recommendations and state.recommendations.recommended_products:
        top = state.recommendations.recommended_products[:3]
        prod_lines = [f"{p.product_name} ({p.product_type}) - suitability {p.suitability_score:.2f}" for p in top]
        points.append("Top recommended products: " + "; ".join(prod_lines))

    if state.recommendations and state.recommendations.portfolio_allocation:
        alloc = state.recommendations.portfolio_allocation
        # show top allocations
        sorted_alloc = sorted(alloc.items(), key=lambda x: x[1], reverse=True)[:3]
        alloc_lines = [f"{k}: {v:.0%}" for k, v in sorted_alloc]
        points.append("Planned allocation: " + ", ".join(alloc_lines))

    return points

def generate_meeting_questions(state: WorkflowState) -> List[str]:
    """Generate relevant questions for prospect."""
    q = [
        "Can you confirm your most important financial goal right now?",
        "How do you feel about short-term portfolio fluctuations?",
        "Do you have any upcoming liquidity needs not yet discussed?"
    ]

    if state.analysis and state.analysis.goal_prediction and state.analysis.goal_prediction.challenges:
        q.append("Which of these challenges do you feel are most relevant: " + ", ".join(state.analysis.goal_prediction.challenges[:3]))

    return q

def generate_meeting_objection_handling(state: WorkflowState) -> Dict[str, str]:
    """Generate responses to common objections."""
    return {
        "market_volatility": "Explain diversification, time horizon benefits and historical recovery patterns.",
        "fees": "Highlight net returns, fee transparency and alignment with goals.",
        "risk": "Show tailored allocation, stress-test scenarios, and downside protections."
    }

def generate_meeting_next_steps(state: WorkflowState) -> List[str]:
    """Generate follow-up action items."""
    steps = [
        "Agree and sign onboarding paperwork",
        "Fund initial allocations",
        "Schedule a follow-up in 30 days to review performance"
    ]

    if state.recommendations and state.recommendations.recommended_products:
        steps.insert(0, "Share detailed product factsheets and suitability notes")

    return steps



