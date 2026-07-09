


"""
Risk Assessment Agent - Assess financial risk profile using ML and AI.
"""

from langraph_agents.base_agent import CriticalAgent
from state import WorkflowState, RiskAssessmentResult, ProspectData
from config import get_settings, get_gemini_model
import logging
from langraph_agents.tools.ml_prediction_tool import predict_risk_profile_tool
from langraph_agents.tools.genai_tool import generate_llm_response
from langraph_agents.tools.calculation_tool import (
    rule_based_risk_assessment,
    generate_rule_based_factors,
    generate_rule_based_recommendations
)

logger = logging.getLogger(__name__)


class RiskAssessmentAgent(CriticalAgent):
    """Assess financial risk profile using ML models and AI analysis."""
    
    def __init__(self, **kwargs):
        settings = get_settings()
        
        # Initialize LLM if API key available
        llm = get_gemini_model(model="gemini-2.5-flash", temperature=settings.default_temperature)
        
        super().__init__(
            name="RiskAssessmentAgent",
            description="Assess financial risk profile",
            llm=llm,
            **kwargs
        )
        self.risk_model = None
        self.label_encoders = None

    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Perform comprehensive risk assessment.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with risk results
        """
        if not state.prospect or not state.prospect.prospect_data:
            raise ValueError("Prospect data is required for risk assessment.")
        prospect_data = state.prospect.prospect_data
        
        # ML-based risk assessment
        ml_result = await self._ml_risk_assessment(prospect_data)
        
        # AI-based risk analysis (if LLM available)
        if self.llm:
            ai_result = await self._ai_risk_analysis(prospect_data, ml_result)
        else:
            ai_result = {
                "risk_factors": generate_rule_based_factors(prospect_data, ml_result),
                "recommendations": generate_rule_based_recommendations(ml_result["risk_level"])
            }
        
        # Combine results
        risk_assessment = RiskAssessmentResult(
            risk_level=ml_result["risk_level"],
            confidence_score=ml_result["confidence"],
            risk_factors=ai_result["risk_factors"],
            recommendations=ai_result["recommendations"]
        )
        
        state.analysis.risk_assessment = risk_assessment
        
        self.logger.info(f"Risk assessment complete: {ml_result['risk_level']} (confidence: {ml_result['confidence']:.2f})")
        
        return state
    
    async def _ml_risk_assessment(self, prospect_data: ProspectData) -> dict:
        """ML-based risk prediction."""
        try:
            # Prepare data
            data_dict = {
                "age": prospect_data.age,
                "annual_income": prospect_data.annual_income,
                "current_savings": prospect_data.current_savings,
                "target_goal_amount": prospect_data.target_goal_amount,
                "investment_horizon_years": prospect_data.investment_horizon_years,
                "number_of_dependents": prospect_data.number_of_dependents,
                "investment_experience_level": prospect_data.investment_experience_level
            }
            
            risk_level, confidence = await predict_risk_profile_tool(data_dict)
            return {
                "risk_level": risk_level,
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"ML prediction tool failed: {e}")
            return rule_based_risk_assessment(prospect_data)
    
    async def _ai_risk_analysis(self, prospect_data: ProspectData, ml_result: dict) -> dict:
        """LLM-based risk factor analysis."""
        try:
            prompt = f"""Analyze the following investor profile and provide risk assessment insights:
 
Age: {prospect_data.age}
Annual Income: ₹{prospect_data.annual_income:,.0f}
Current Savings: ₹{prospect_data.current_savings:,.0f}
Target Goal: ₹{prospect_data.target_goal_amount:,.0f}
Investment Horizon: {prospect_data.investment_horizon_years} years
Dependents: {prospect_data.number_of_dependents}
Experience Level: {prospect_data.investment_experience_level}
ML Predicted Risk Level: {ml_result['risk_level']}
 
Provide:
1. Three specific risk factors (one per line, starting with "- ")
2. Three actionable recommendations (one per line, starting with "- ")
 
Format your response as:
RISK FACTORS:
- Factor 1
- Factor 2
- Factor 3
 
RECOMMENDATIONS:
- Recommendation 1
- Recommendation 2
- Recommendation 3
"""
            
            response = generate_llm_response(self.llm, prompt, {})
            
            # Parse response
            lines = response.split('\n')
            risk_factors = []
            recommendations = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if 'RISK FACTORS' in line:
                    current_section = 'factors'
                elif 'RECOMMENDATIONS' in line:
                    current_section = 'recommendations'
                elif line.startswith('-'):
                    text = line[1:].strip()
                    if current_section == 'factors':
                        risk_factors.append(text)
                    elif current_section == 'recommendations':
                        recommendations.append(text)
            
            return {
                "risk_factors": risk_factors if risk_factors else generate_rule_based_factors(prospect_data, ml_result),
                "recommendations": recommendations if recommendations else generate_rule_based_recommendations(ml_result['risk_level'])
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {
                "risk_factors": generate_rule_based_factors(prospect_data, ml_result),
                "recommendations": generate_rule_based_recommendations(ml_result['risk_level'])
            }

