
"""
State models for the RM-AgenticAI-LangGraph workflow.
Defines all Pydantic models for type safety and validation.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ProspectData(BaseModel):
    """Individual prospect information."""
    prospect_id: str = Field(description="Unique prospect identifier")
    name: str = Field(description="Prospect name")
    age: int = Field(description="Age in years", ge=18, le=100)
    annual_income: float = Field(description="Annual income amount", ge=0)
    current_savings: float = Field(description="Current savings amount", ge=0)
    target_goal_amount: float = Field(description="Investment goal amount", ge=0)
    investment_horizon_years: int = Field(description="Years to goal", ge=1)
    number_of_dependents: int = Field(description="Number of dependents", ge=0)
    investment_experience_level: str = Field(description="Experience level: Beginner, Intermediate, Advanced")
    investment_goal: Optional[str] = Field(default=None, description="Investment goal description")


class RiskAssessmentResult(BaseModel):
    """Risk assessment analysis results."""
    risk_level: str = Field(description="Risk level: Low, Moderate, High")
    confidence_score: float = Field(description="Confidence 0.0-1.0", ge=0.0, le=1.0)
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    recommendations: List[str] = Field(default_factory=list, description="Risk mitigation recommendations")


class GoalPredictionResult(BaseModel):
    """Goal success prediction results."""
    goal_success: str = Field(description="Likely or Unlikely")
    probability: float = Field(description="Success probability 0.0-1.0", ge=0.0, le=1.0)
    success_factors: List[str] = Field(default_factory=list, description="Success enabling factors")
    challenges: List[str] = Field(default_factory=list, description="Potential obstacles")
    timeline_analysis: Dict[str, Any] = Field(default_factory=dict, description="Timeline feasibility")


class PersonaResult(BaseModel):
    """Investor personality classification."""
    persona_type: str = Field(description="Aggressive Growth, Steady Saver, Cautious Planner")
    confidence_score: float = Field(description="Classification confidence", ge=0.0, le=1.0)
    characteristics: List[str] = Field(default_factory=list, description="Persona traits")
    behavioral_insights: List[str] = Field(default_factory=list, description="Behavioral insights")


class ProductRecommendation(BaseModel):
    """Single product recommendation with scoring."""
    product_id: str = Field(description="Product identifier")
    product_name: str = Field(description="Product name")
    product_type: str = Field(description="Product type category")
    suitability_score: float = Field(description="Match score 0.0-1.0", ge=0.0, le=1.0)
    justification: str = Field(description="Recommendation justification")
    risk_alignment: str = Field(description="Risk alignment statement")
    expected_returns: str = Field(description="Expected return range")
    fees: str = Field(description="Fee structure")


class MeetingGuide(BaseModel):
    """Meeting preparation guide."""
    agenda_items: List[str] = Field(default_factory=list)
    key_talking_points: List[str] = Field(default_factory=list)
    questions_to_ask: List[str] = Field(default_factory=list)
    objection_handling: Dict[str, str] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)
    estimated_duration: str = Field(default="45 minutes")


class ComplianceCheck(BaseModel):
    """Regulatory compliance validation."""
    is_compliant: bool = Field(description="Meets all requirements")
    compliance_score: float = Field(description="Compliance score 0.0-1.0", ge=0.0, le=1.0)
    violations: List[str] = Field(default_factory=list, description="Regulatory violations")
    warnings: List[str] = Field(default_factory=list, description="Compliance warnings")
    required_disclosures: List[str] = Field(default_factory=list, description="Required disclosures")


class AgentExecution(BaseModel):
    """Agent execution tracking."""
    agent_name: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = Field(default="running")  # running, completed, failed
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class ProspectState(BaseModel):
    """Prospect data and validation state."""
    prospect_data: Optional[ProspectData] = None
    validation_errors: List[str] = Field(default_factory=list)
    data_quality_score: Optional[float] = None
    missing_fields: List[str] = Field(default_factory=list)


class AnalysisState(BaseModel):
    """Analysis results state."""
    risk_assessment: Optional[RiskAssessmentResult] = None
    goal_prediction: Optional[GoalPredictionResult] = None
    persona_classification: Optional[PersonaResult] = None


class RecommendationState(BaseModel):
    """Recommendation results state."""
    recommended_products: List[ProductRecommendation] = Field(default_factory=list)
    portfolio_allocation: Dict[str, float] = Field(default_factory=dict)
    compliance_check: Optional[ComplianceCheck] = None


class MeetingState(BaseModel):
    """Meeting preparation state."""
    meeting_guide: Optional[MeetingGuide] = None
    presentation_slides: List[Dict[str, Any]] = Field(default_factory=list)
    client_materials: List[str] = Field(default_factory=list)


class ChatState(BaseModel):
    """Chat interaction state."""
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    current_query: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    response: Optional[str] = None


class WorkflowState(BaseModel):
    """Complete workflow state container."""
    
    # Identifiers
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Sub-states
    prospect: ProspectState = Field(default_factory=ProspectState)
    analysis: AnalysisState = Field(default_factory=AnalysisState)
    recommendations: RecommendationState = Field(default_factory=RecommendationState)
    meeting: MeetingState = Field(default_factory=MeetingState)
    chat: ChatState = Field(default_factory=ChatState)
    
    # Execution Tracking
    agent_executions: List[AgentExecution] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    current_step: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Final Results
    overall_confidence: Optional[float] = None
    key_insights: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_agent_execution(self, agent_name: str) -> AgentExecution:
        """Record agent execution start."""
        execution = AgentExecution(agent_name=agent_name)
        self.agent_executions.append(execution)
        return execution
    
    def complete_agent_execution(self, agent_name: str, success: bool = True, error: Optional[str] = None):
        """Mark agent execution as complete."""
        for execution in reversed(self.agent_executions):
            if execution.agent_name == agent_name and execution.status == "running":
                execution.end_time = datetime.now()
                execution.status = "completed" if success else "failed"
                execution.error_message = error
                if execution.start_time and execution.end_time:
                    execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
                break
        
        if success:
            if agent_name not in self.completed_steps:
                self.completed_steps.append(agent_name)
        else:
            if agent_name not in self.failed_steps:
                self.failed_steps.append(agent_name)
        
        self.updated_at = datetime.now()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Calculate performance statistics."""
        total = len(self.agent_executions)
        completed = len([e for e in self.agent_executions if e.status == "completed"])
        failed = len([e for e in self.agent_executions if e.status == "failed"])
        
        execution_times = [e.execution_time for e in self.agent_executions if e.execution_time]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "average_execution_time": avg_time,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps
        }
