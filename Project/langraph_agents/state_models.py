# TODO: Import all necessary pydantic and typing modules
# TODO: Define all state model classes mirroring state.py but for agent internal use
# TODO: Include validation logic for state transitions
# TODO: Add serialization methods for logging and debugging


# Agent-facing, lightweight state models (mirrors Project/state.py structures)
# Provides small helpers for serialization and transition validation used by agents.

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json
import uuid


class ProspectDataModel(BaseModel):
    prospect_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[float] = None
    current_savings: Optional[float] = None
    target_goal_amount: Optional[float] = None
    investment_horizon_years: Optional[int] = None
    number_of_dependents: Optional[int] = None
    investment_experience_level: Optional[str] = None
    investment_goal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.dict()


class RiskAssessmentModel(BaseModel):
    risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    @validator("confidence_score")
    def clamp_confidence(cls, v):
        if v is None:
            return v
        return max(0.0, min(1.0, float(v)))


class GoalPredictionModel(BaseModel):
    goal_success: Optional[str] = None
    probability: Optional[float] = None
    success_factors: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    timeline_analysis: Dict[str, Any] = Field(default_factory=dict)

    @validator("probability")
    def clamp_prob(cls, v):
        if v is None:
            return v
        return max(0.0, min(1.0, float(v)))


class PersonaModel(BaseModel):
    persona_type: Optional[str] = None
    confidence_score: Optional[float] = None
    characteristics: List[str] = Field(default_factory=list)
    behavioral_insights: List[str] = Field(default_factory=list)


class ProductRecommendationModel(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    suitability_score: Optional[float] = None
    justification: Optional[str] = None
    risk_alignment: Optional[str] = None
    expected_returns: Optional[str] = None
    fees: Optional[str] = None


class MeetingGuideModel(BaseModel):
    agenda_items: List[str] = Field(default_factory=list)
    key_talking_points: List[str] = Field(default_factory=list)
    questions_to_ask: List[str] = Field(default_factory=list)
    objection_handling: Dict[str, str] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)
    estimated_duration: str = Field(default="45 minutes")


class ComplianceCheckModel(BaseModel):
    is_compliant: bool = Field(default=True)
    compliance_score: Optional[float] = None
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    required_disclosures: List[str] = Field(default_factory=list)


class AgentExecutionModel(BaseModel):
    agent_name: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = Field(default="running")
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

    def complete(self, success: bool = True, error: Optional[str] = None):
        self.end_time = datetime.utcnow()
        self.status = "completed" if success else "failed"
        self.error_message = error
        if self.start_time and self.end_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()


class ProspectStateModel(BaseModel):
    prospect_data: Optional[ProspectDataModel] = None
    validation_errors: List[str] = Field(default_factory=list)
    data_quality_score: Optional[float] = None
    missing_fields: List[str] = Field(default_factory=list)


class AnalysisStateModel(BaseModel):
    risk_assessment: Optional[RiskAssessmentModel] = None
    goal_prediction: Optional[GoalPredictionModel] = None
    persona_classification: Optional[PersonaModel] = None


class RecommendationStateModel(BaseModel):
    recommended_products: List[ProductRecommendationModel] = Field(default_factory=list)
    portfolio_allocation: Dict[str, float] = Field(default_factory=dict)
    compliance_check: Optional[ComplianceCheckModel] = None


class MeetingStateModel(BaseModel):
    meeting_guide: Optional[MeetingGuideModel] = None
    presentation_slides: List[Dict[str, Any]] = Field(default_factory=list)
    client_materials: List[str] = Field(default_factory=list)


class ChatStateModel(BaseModel):
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_query: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    response: Optional[str] = None


class WorkflowStateModel(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None

    prospect: ProspectStateModel = Field(default_factory=ProspectStateModel)
    analysis: AnalysisStateModel = Field(default_factory=AnalysisStateModel)
    recommendations: RecommendationStateModel = Field(default_factory=RecommendationStateModel)
    meeting: MeetingStateModel = Field(default_factory=MeetingStateModel)
    chat: ChatStateModel = Field(default_factory=ChatStateModel)

    agent_executions: List[AgentExecutionModel] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    current_step: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    overall_confidence: Optional[float] = None
    key_insights: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)

    config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def start_agent(self, agent_name: str) -> AgentExecutionModel:
        exec_record = AgentExecutionModel(agent_name=agent_name)
        self.agent_executions.append(exec_record)
        self.current_step = agent_name
        self.updated_at = datetime.utcnow()
        return exec_record

    def finish_agent(self, agent_name: str, success: bool = True, error: Optional[str] = None):
        for e in reversed(self.agent_executions):
            if e.agent_name == agent_name and e.status == "running":
                e.complete(success=success, error=error)
                break
        if success:
            if agent_name not in self.completed_steps:
                self.completed_steps.append(agent_name)
        else:
            if agent_name not in self.failed_steps:
                self.failed_steps.append(agent_name)
        self.current_step = None
        self.updated_at = datetime.utcnow()

    def execution_summary(self) -> Dict[str, Any]:
        total = len(self.agent_executions)
        completed = len([e for e in self.agent_executions if e.status == "completed"])
        failed = len([e for e in self.agent_executions if e.status == "failed"])
        times = [e.execution_time for e in self.agent_executions if e.execution_time]
        avg = sum(times) / len(times) if times else 0
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total) if total else 0,
            "average_time": avg,
        }

    def to_json(self) -> str:
        return self.json()

    @classmethod
    def from_json(cls, payload: str) -> "WorkflowStateModel":
        data = json.loads(payload)
        return cls.parse_obj(data)


# Simple transition validator used by agents when updating shared state
def validate_transition(current: WorkflowStateModel, proposed: WorkflowStateModel) -> bool:
    # Example: do not allow clearing prospect data
    if current.prospect.prospect_data and not proposed.prospect.prospect_data:
        return False
    return True
