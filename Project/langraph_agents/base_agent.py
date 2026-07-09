

"""
Abstract base class for all agents.
Provides common functionality for execution, validation, and monitoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from config import get_logger
from state import WorkflowState

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import BaseLanguageModel
except ImportError:
    ChatGoogleGenerativeAI = None
    ChatPromptTemplate = None
    BaseLanguageModel = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        llm: Optional[Any] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        """
        Initialize agent with configuration.
        
        Args:
            name: Agent identifier
            description: Agent description
            llm: Language model instance (optional)
            temperature: LLM creativity parameter
            max_tokens: Max output token limit
        """
        self.name = name
        self.description = description
        self.llm = llm
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = get_logger(f"agent.{name}")
        
        # Performance tracking
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.created_at = datetime.now()
        
        self.logger.info(f"Initialized {name} agent")
    
    @abstractmethod
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute main agent logic (must be implemented by subclasses).
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    def validate_input(self, state: WorkflowState) -> bool:
        """
        Validate input state before execution.
        
        Args:
            state: Workflow state to validate
            
        Returns:
            True if valid, False otherwise
        """
        if state is None:
            self.logger.error("State is None")
            return False
        return True
    
    def validate_output(self, state: WorkflowState) -> bool:
        """
        Validate output state after execution.
        
        Args:
            state: Workflow state to validate
            
        Returns:
            True if valid, False otherwise
        """
        if state is None:
            self.logger.error("Output state is None")
            return False
        return True
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """
        Execute with error handling and monitoring.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        self.execution_count += 1
        
        try:
            # Validate input
            if not self.validate_input(state):
                raise ValueError(f"{self.name}: Input validation failed")
            
            self.logger.info(f"{self.name}: Starting execution")
            
            # Execute main logic
            result_state = await self.execute(state)
            
            # Validate output
            if not self.validate_output(result_state):
                raise ValueError(f"{self.name}: Output validation failed")
            
            # Track success
            self.success_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time
            
            self.logger.info(f"{self.name}: Completed in {execution_time:.2f}s")
            
            return result_state
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"{self.name}: Execution failed - {str(e)}")
            raise
    
    def generate_response(self, prompt_template: Any, input_variables: Dict[str, Any]) -> str:
        """
        Invoke LLM with prompt and variables.
        
        Args:
            prompt_template: Formatted prompt
            input_variables: Variables for template
            
        Returns:
            String response from LLM
        """
        try:
            if self.llm is None:
                raise ValueError("LLM not configured for this agent")
            
            # Format prompt
            if hasattr(prompt_template, 'format'):
                formatted_prompt = prompt_template.format(**input_variables)
            else:
                formatted_prompt = str(prompt_template)
            
            # Invoke LLM
            if hasattr(self.llm, 'invoke'):
                response = self.llm.invoke(formatted_prompt)
                if hasattr(response, 'content'):
                    return response.content.strip()
                return str(response).strip()
            else:
                # Fallback for simple callable
                return str(self.llm(formatted_prompt)).strip()
                
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Return execution statistics."""
        avg_time = self.total_execution_time / self.execution_count if self.execution_count > 0 else 0
        success_rate = self.success_count / self.execution_count if self.execution_count > 0 else 0
        
        return {
            "agent_name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "average_execution_time": avg_time,
            "total_execution_time": self.total_execution_time,
            "created_at": self.created_at
        }
    
    def reset_metrics(self):
        """Clear performance statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0


class CriticalAgent(BaseAgent):
    """Agent that must succeed for workflow continuation."""
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute with exception re-raising."""
        try:
            return await super().run(state)
        except Exception as e:
            self.logger.error(f"Critical agent {self.name} failed: {str(e)}")
            raise  # Re-raise to stop workflow


class OptionalAgent(BaseAgent):
    """Agent that can fail gracefully."""
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute with graceful error handling."""
        try:
            return await super().run(state)
        except Exception as e:
            self.logger.warning(f"Optional agent {self.name} failed: {str(e)}")
            # Return state unchanged
            return state
