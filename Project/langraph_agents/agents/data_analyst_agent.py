# TODO: Create DataAnalystAgent class inheriting from BaseAgent
# TODO: Implement validate_prospect_data method checking required fields
# TODO: Implement check_for_errors method identifying invalid data patterns
# TODO: Implement calculate_quality_score method based on completeness and validity
# TODO: Implement identify_missing_fields method listing absent required data
# TODO: Implement async run method:
#   - Validate prospect data presence
#   - Check for data errors
#   - Calculate quality score
#   - Identify missing fields
#   - Update state with validation_errors and data_quality_score
#   - Return updated state


"""
Data Analyst Agent - Validates prospect data quality and completeness.
"""

from langraph_agents.base_agent import CriticalAgent
from state import WorkflowState
from langraph_agents.tools.data_processing_tool import validate_prospect_data


class DataAnalystAgent(CriticalAgent):
    """Validates and enhances prospect data quality."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="DataAnalystAgent",
            description="Validates data quality and completeness",
            **kwargs
        )
    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Validate and enhance prospect data.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with validation results
        """
        self.logger.info("Starting data validation")
        
        # Get prospect data
        prospect_data = state.prospect.prospect_data
        
        if not prospect_data:
            raise ValueError("No prospect data provided")
        
        # Perform validation
        validation_results = validate_prospect_data(prospect_data)
        
        # Update state
        state.prospect.validation_errors = validation_results["errors"]
        state.prospect.missing_fields = validation_results["missing_fields"]
        state.prospect.data_quality_score = validation_results["quality_score"]
        
        self.logger.info(f"Data quality score: {validation_results['quality_score']:.2f}")
        
        return state
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Check prospect data exists."""
        if not super().validate_input(state):
            return False
        
        if state.prospect.prospect_data is None:
            self.logger.error("No prospect data in state")
            return False
        
        return True
    
    def validate_output(self, state: WorkflowState) -> bool:
        """Verify data quality score is set."""
        if not super().validate_output(state):
            return False
        
        if state.prospect.data_quality_score is None:
            self.logger.error("Data quality score not set")
            return False
        
        return True
