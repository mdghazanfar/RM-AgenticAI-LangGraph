"""
LangGraph workflow orchestration for prospect analysis.
Coordinates multiple agents in a sequential processing pipeline.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import WorkflowState, ProspectData, ProspectState
from langraph_agents.agents.data_analyst_agent import DataAnalystAgent
from langraph_agents.agents.risk_assessment_agent import RiskAssessmentAgent
from langraph_agents.agents.goal_planning_agent import GoalPlanningAgent
from langraph_agents.agents.persona_agent import PersonaAgent
from langraph_agents.agents.product_specialist_agent import ProductSpecialistAgent
from langraph_agents.agents.portfolio_optimizer_agent import PortfolioOptimizerAgent
from langraph_agents.agents.compliance_agent import ComplianceAgent
from langraph_agents.agents.meeting_coordinator_agent import MeetingCoordinatorAgent
from config import get_logger


class ProspectAnalysisWorkflow:
    """
    Multi-agent workflow for comprehensive prospect analysis.
    Orchestrates 9 sequential processing nodes.
    """
    
    def __init__(self):
        """Initialize workflow and agents."""
        self.logger = get_logger("ProspectAnalysisWorkflow")
        
        # Initialize agents
        self.data_analyst = DataAnalystAgent()
        self.risk_assessor = RiskAssessmentAgent()
        self.goal_planner = GoalPlanningAgent()
        self.persona_classifier = PersonaAgent()
        self.product_specialist = ProductSpecialistAgent()
        self.portfolio_optimizer = PortfolioOptimizerAgent()
        self.compliance_checker = ComplianceAgent()
        self.meeting_coordinator = MeetingCoordinatorAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        self.logger.info("Workflow initialized with 8 agents")
    
    def _build_workflow(self) -> StateGraph:
        """Construct LangGraph StateGraph with all nodes and edges."""
        
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("data_analysis", self._data_analysis_node)
        workflow.add_node("risk_assessment", self._risk_assessment_node)
        workflow.add_node("goal_planning", self._goal_planning_node)
        workflow.add_node("persona_classification", self._persona_classification_node)
        workflow.add_node("product_recommendation", self._product_recommendation_node)
        workflow.add_node("portfolio_optimization", self._portfolio_optimization_node)
        workflow.add_node("compliance_check", self._compliance_check_node)
        workflow.add_node("meeting_coordination", self._meeting_coordination_node)
        workflow.add_node("finalize_analysis", self._finalize_analysis_node)
        
        # Set entry point   
        workflow.set_entry_point("data_analysis")
        
        # Define edges (sequential flow)
        workflow.add_edge("data_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "goal_planning")
        workflow.add_edge("goal_planning", "persona_classification")
        workflow.add_edge("persona_classification", "product_recommendation")
        workflow.add_edge("product_recommendation", "portfolio_optimization")
        workflow.add_edge("portfolio_optimization", "compliance_check")
        workflow.add_edge("compliance_check", "meeting_coordination")
        workflow.add_edge("meeting_coordination", "finalize_analysis")
        workflow.add_edge("finalize_analysis", END)
        
        # Compile with checkpoint
        checkpointer = MemorySaver()
        compiled = workflow.compile(checkpointer=checkpointer)
        
        self.logger.info("Workflow graph compiled successfully")
        
        return compiled
    
    async def _data_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Node 1: Validate data quality and completeness."""
        self.logger.info("Executing data_analysis node")
        
        state.current_step = "data_analysis"
        state.add_agent_execution("DataAnalystAgent")
        
        try:
            result_state = await self.data_analyst.run(state)
            state.complete_agent_execution("DataAnalystAgent", success=True)
            state.completed_steps.append("data_analysis")
            return result_state
        except Exception as e:
            state.complete_agent_execution("DataAnalystAgent", success=False, error=str(e))
            state.failed_steps.append("data_analysis")
            raise
    
    async def _risk_assessment_node(self, state: WorkflowState) -> WorkflowState:
        """Node 2: Assess financial risk profile."""
        self.logger.info("Executing risk_assessment node")
        
        if "data_analysis" not in state.completed_steps:
            raise ValueError("Data analysis must complete before risk assessment")
        
        state.current_step = "risk_assessment"
        state.add_agent_execution("RiskAssessmentAgent")
        
        try:
            result_state = await self.risk_assessor.run(state)
            state.complete_agent_execution("RiskAssessmentAgent", success=True)
            state.completed_steps.append("risk_assessment")
            return result_state
        except Exception as e:
            state.complete_agent_execution("RiskAssessmentAgent", success=False, error=str(e))
            state.failed_steps.append("risk_assessment")
            raise

    async def _goal_planning_node(self, state: WorkflowState) -> WorkflowState:
        """Node 3: Assess goal feasibility and timeline."""
        self.logger.info("Executing goal_planning node")
        
        state.current_step = "goal_planning"
        state.add_agent_execution("GoalPlanningAgent")
        
        try:
            result_state = await self.goal_planner.run(state)
            state.complete_agent_execution("GoalPlanningAgent", success=True)
            state.completed_steps.append("goal_planning")
            return result_state
        except Exception as e:
            self.logger.warning(f"Goal planning failed: {e}")
            state.complete_agent_execution("GoalPlanningAgent", success=False, error=str(e))
            return state
    
    async def _persona_classification_node(self, state: WorkflowState) -> WorkflowState:
        """Node 4: Classify investor personality type."""
        self.logger.info("Executing persona_classification node")
        
        state.current_step = "persona_classification"
        state.add_agent_execution("PersonaAgent")
        
        try:
            result_state = await self.persona_classifier.run(state)
            state.complete_agent_execution("PersonaAgent", success=True)
            state.completed_steps.append("persona_classification")
            return result_state
        except Exception as e:
            self.logger.warning(f"Persona classification failed: {e}")
            state.complete_agent_execution("PersonaAgent", success=False, error=str(e))
            return state
    
    async def _product_recommendation_node(self, state: WorkflowState) -> WorkflowState:
        """Node 5: Generate intelligent product recommendations."""
        self.logger.info("Executing product_recommendation node")
        
        if "risk_assessment" not in state.completed_steps:
            raise ValueError("Risk assessment must complete before product recommendation")
        
        state.current_step = "product_recommendation"
        state.add_agent_execution("ProductSpecialistAgent")
        
        try:
            result_state = await self.product_specialist.run(state)
            state.complete_agent_execution("ProductSpecialistAgent", success=True)
            state.completed_steps.append("product_recommendation")
            return result_state
        except Exception as e:
            state.complete_agent_execution("ProductSpecialistAgent", success=False, error=str(e))
            state.failed_steps.append("product_recommendation")
            raise

    async def _portfolio_optimization_node(self, state: WorkflowState) -> WorkflowState:
        """Node 6: Optimize product allocations."""
        self.logger.info("Executing portfolio_optimization node")
        
        state.current_step = "portfolio_optimization"
        state.add_agent_execution("PortfolioOptimizerAgent")
        
        try:
            result_state = await self.portfolio_optimizer.run(state)
            state.complete_agent_execution("PortfolioOptimizerAgent", success=True)
            state.completed_steps.append("portfolio_optimization")
            return result_state
        except Exception as e:
            self.logger.warning(f"Portfolio optimization failed: {e}")
            state.complete_agent_execution("PortfolioOptimizerAgent", success=False, error=str(e))
            return state

    async def _compliance_check_node(self, state: WorkflowState) -> WorkflowState:
        """Node 7: Perform suitability and regulatory compliance checks."""
        self.logger.info("Executing compliance_check node")
        
        state.current_step = "compliance_check"
        state.add_agent_execution("ComplianceAgent")
        
        try:
            result_state = await self.compliance_checker.run(state)
            state.complete_agent_execution("ComplianceAgent", success=True)
            state.completed_steps.append("compliance_check")
            return result_state
        except Exception as e:
            state.complete_agent_execution("ComplianceAgent", success=False, error=str(e))
            state.failed_steps.append("compliance_check")
            raise

    async def _meeting_coordination_node(self, state: WorkflowState) -> WorkflowState:
        """Node 8: Prepare meeting materials and guide."""
        self.logger.info("Executing meeting_coordination node")
        
        state.current_step = "meeting_coordination"
        state.add_agent_execution("MeetingCoordinatorAgent")
        
        try:
            result_state = await self.meeting_coordinator.run(state)
            state.complete_agent_execution("MeetingCoordinatorAgent", success=True)
            state.completed_steps.append("meeting_coordination")
            return result_state
        except Exception as e:
            self.logger.warning(f"Meeting coordination failed: {e}")
            state.complete_agent_execution("MeetingCoordinatorAgent", success=False, error=str(e))
            return state
    
    async def _finalize_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Node 9: Generate summary, insights, and action items."""
        self.logger.info("Executing finalize_analysis node")
        
        state.current_step = "finalize_analysis"
        
        try:
            # Calculate overall confidence
            confidence_scores = []
            
            if state.analysis.risk_assessment:
                confidence_scores.append(state.analysis.risk_assessment.confidence_score)
            
            if state.analysis.persona_classification:
                confidence_scores.append(state.analysis.persona_classification.confidence_score)
            
            if state.prospect.data_quality_score:
                confidence_scores.append(state.prospect.data_quality_score)
            
            state.overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            # Generate key insights
            state.key_insights = self._generate_key_insights(state)
            
            # Generate action items
            state.action_items = self._generate_action_items(state)
            
            # Update timestamp
            state.updated_at = datetime.now()
            
            state.completed_steps.append("finalize_analysis")
            
            self.logger.info(f"Analysis finalized with {len(state.key_insights)} insights")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Finalization failed: {e}")
            state.failed_steps.append("finalize_analysis")
            return state
    
    def _generate_key_insights(self, state: WorkflowState) -> List[str]:
        """Extract key findings from complete analysis."""
        insights = []
        
        if state.prospect.data_quality_score is not None:
            quality = state.prospect.data_quality_score
            if quality >= 0.9:
                insights.append(f"Excellent data quality (score: {quality:.2f})")
            elif quality >= 0.7:
                insights.append(f"Good data quality (score: {quality:.2f})")
            else:
                insights.append(f"Data quality issues (score: {quality:.2f})")
        
        if state.analysis.risk_assessment:
            risk = state.analysis.risk_assessment
            insights.append(
                f"Risk: {risk.risk_level} ({risk.confidence_score:.0%} confidence)"
            )
        
        if state.analysis.goal_prediction:
            gp = state.analysis.goal_prediction
            insights.append(f"Goal success probability: {gp.probability:.0%} - {gp.goal_success}")

        if state.analysis.persona_classification:
            persona = state.analysis.persona_classification
            insights.append(f"Persona: {persona.persona_type}")
        
        if state.recommendations.recommended_products:
            top = state.recommendations.recommended_products[0]
            insights.append(f"Top product: {top.product_name} ({top.suitability_score:.0%})")

        if state.recommendations.compliance_check:
            cc = state.recommendations.compliance_check
            compliance_status = "Compliant" if cc.is_compliant else "Non-Compliant"
            insights.append(f"Compliance: {compliance_status} (Score: {cc.compliance_score:.2f})")
        
        return insights
    
    def _generate_action_items(self, state: WorkflowState) -> List[str]:
        """Create relationship manager action items."""
        actions = []
        
        if state.prospect.validation_errors:
            actions.append(f"Address {len(state.prospect.validation_errors)} validation issues")
        
        if state.analysis.risk_assessment:
            risk_level = state.analysis.risk_assessment.risk_level
            if risk_level == "High":
                actions.append("Schedule risk tolerance discussion")
            elif risk_level == "Low":
                actions.append("Discuss capital preservation objectives")
            else:
                actions.append("Review balanced investment strategy")
        
        if state.recommendations.recommended_products:
            actions.append(f"Prepare materials for {len(state.recommendations.recommended_products)} products")

        if state.recommendations.compliance_check and not state.recommendations.compliance_check.is_compliant:
            actions.append(f"Resolve compliance violations: {', '.join(state.recommendations.compliance_check.violations[:2])}")
        
        if state.meeting.meeting_guide:
            actions.append("Review client meeting guide and prepare talking points")
        
        actions.append("Schedule follow-up meeting within 7 days")
        
        return actions
    
    async def analyze_prospect(
        self,
        prospect_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> WorkflowState:
        """Execute complete workflow for a prospect."""
        self.logger.info(f"Starting analysis for {prospect_data.get('name')}")
        
        initial_state = WorkflowState(
            session_id=session_id or str(uuid.uuid4()),
            prospect=ProspectState(
                prospect_data=ProspectData(**prospect_data)
            )
        )
        
        config = {
            "configurable": {
                "thread_id": initial_state.session_id
            }
        }
        
        try:
            final_state = await self.workflow.ainvoke(initial_state, config)
            # Ensure final_state is a WorkflowState instance
            if isinstance(final_state, dict):
                try:
                    final_state = WorkflowState.parse_obj(final_state)
                except Exception:
                    final_state = WorkflowState(**final_state)

            if not isinstance(final_state, WorkflowState):
                try:
                    final_state = WorkflowState.parse_obj(final_state)
                except Exception:
                    pass

            self.logger.info("Analysis completed successfully")
            return final_state
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            raise
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Return workflow metadata."""
        return {
            "name": "ProspectAnalysisWorkflow",
            "agents": ["DataAnalyst", "RiskAssessor", "GoalPlanner", "Persona", "ProductSpecialist", "PortfolioOptimizer", "ComplianceChecker", "MeetingCoordinator"],
            "steps": ["data_analysis", "risk_assessment", "goal_planning", "persona_classification", 
                     "product_recommendation", "portfolio_optimization", "compliance_check", "meeting_coordination", "finalize_analysis"]
        }
