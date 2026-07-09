# TODO: Create PersonaAgent class inheriting from BaseAgent
# TODO: Implement classify_persona method determining investor type
# TODO: Implement generate_insights method creating behavioral insights
# TODO: Implement extract_behavioral_signals from prospect data
# TODO: Implement persona classification logic (Aggressive Growth, Steady Saver, Cautious Planner)
# TODO: Implement async run method:
#   - Extract behavioral signals from prospect data
#   - Classify persona type using AI analysis
#   - Generate behavioral characteristics
#   - Create behavioral insights
#   - Calculate confidence score
#   - Return PersonaResult in state



"""
Persona Agent - Classify investor personality type.
"""

from typing import Dict, List, Optional
from langraph_agents.base_agent import OptionalAgent
from state import WorkflowState, PersonaResult, ProspectData, RiskAssessmentResult
from config import get_settings, get_gemini_model
from langraph_agents.tools.genai_tool import generate_llm_response
from langraph_agents.tools.calculation_tool import (
    rule_based_persona_classification,
    get_persona_characteristics,
    calculate_persona_confidence_score,
    get_default_behavioral_insights
)


class PersonaAgent(OptionalAgent):
    """Classify investor personality type and behavioral patterns."""
    
    def __init__(self, **kwargs):
        settings = get_settings()
        
        llm = get_gemini_model(model="gemini-2.5-flash-lite", temperature=settings.default_temperature)
        
        super().__init__(
            name="PersonaAgent",
            description="Classify investor personality",
            llm=llm,
            **kwargs
        )
    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Classify persona and generate insights."""
        self.logger.info("Starting persona classification")
        
        if not state.prospect or not state.prospect.prospect_data:
            self.logger.warning("No prospect data available for persona classification")
            return state
            
        prospect_data = state.prospect.prospect_data
        risk_assessment = state.analysis.risk_assessment if state.analysis else None
        
        # Classify persona
        persona_type = await self._classify_persona(prospect_data, risk_assessment)
        
        # Generate insights
        characteristics = get_persona_characteristics(persona_type)
        behavioral_insights = await self._generate_behavioral_insights(
            persona_type, prospect_data, risk_assessment
        )
        
        # Calculate confidence
        confidence_score = calculate_persona_confidence_score(prospect_data, persona_type)
        
        # Create result
        persona_result = PersonaResult(
            persona_type=persona_type,
            confidence_score=confidence_score,
            characteristics=characteristics,
            behavioral_insights=behavioral_insights
        )
        
        if not state.analysis:
            from state import AnalysisState
            state.analysis = AnalysisState()
        state.analysis.persona_classification = persona_result
        
        self.logger.info(f"Persona classified: {persona_type} (confidence: {confidence_score:.2f})")
        
        return state
    
    async def _classify_persona(
        self,
        prospect_data: ProspectData,
        risk_assessment: Optional[RiskAssessmentResult]
    ) -> str:
        """Classify persona type."""
        if self.llm:
            try:
                prompt = f"""Classify the investor personality type based on this profile:

Age: {prospect_data.age}
Income: ₹{prospect_data.annual_income:,.0f}
Horizon: {prospect_data.investment_horizon_years} years
Experience: {prospect_data.investment_experience_level}
Risk Level: {risk_assessment.risk_level if risk_assessment else 'Unknown'}

Choose ONE of these personas:
1. Aggressive Growth - High risk, long horizon, growth-focused
2. Steady Saver - Balanced, consistent, goal-oriented
3. Cautious Planner - Conservative, capital preservation, low risk

Respond with ONLY the persona name, nothing else."""
                
                response = generate_llm_response(self.llm, prompt, {})
                response_lower = response.lower()
                
                if "aggressive" in response_lower:
                    return "Aggressive Growth"
                elif "cautious" in response_lower or "conservative" in response_lower:
                    return "Cautious Planner"
                elif "steady" in response_lower or "saver" in response_lower:
                    return "Steady Saver"
                else:
                    return "Steady Saver"
                    
            except Exception as e:
                self.logger.warning(f"AI classification failed: {e}")
        
        # Rule-based fallback
        risk_level = risk_assessment.risk_level if risk_assessment else None
        return rule_based_persona_classification(prospect_data, risk_level)
    
    async def _generate_behavioral_insights(
        self,
        persona_type: str,
        prospect_data: ProspectData,
        risk_assessment: Optional[RiskAssessmentResult]
    ) -> List[str]:
        """Generate behavioral insights."""
        if self.llm:
            try:
                prompt = f"""Generate 3 behavioral insights for a {persona_type} investor:

Profile: Age {prospect_data.age}, {prospect_data.investment_experience_level} experience
Risk Level: {risk_assessment.risk_level if risk_assessment else 'Moderate'}

Provide 3 specific insights (one per line, starting with "- ")."""
                
                response = generate_llm_response(self.llm, prompt, {})
                
                insights = []
                for line in response.split('\n'):
                    line_stripped = line.strip()
                    if line_stripped.startswith(('-', '*')):
                        insights.append(line_stripped[1:].strip())
                    elif line_stripped.startswith(('1.', '2.', '3.')):
                        insights.append(line_stripped[2:].strip())
                
                # Fill to 3 insights if we have some but not 3
                if len(insights) > 0:
                    if len(insights) < 3:
                        defaults = get_default_behavioral_insights(persona_type)
                        insights.extend(defaults[:3 - len(insights)])
                    return insights[:3]
                    
            except Exception as e:
                self.logger.warning(f"AI insights generation failed: {e}")
        
        # Default insights
        return get_default_behavioral_insights(persona_type)
