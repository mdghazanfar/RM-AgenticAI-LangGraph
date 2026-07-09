from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger("tools.genai_tool")

def generate_llm_response(llm: Any, prompt_template: Any, input_variables: Dict[str, Any]) -> str:
    """
    Invoke LLM with formatted prompt and variables.
    
    Args:
        llm: The language model instance
        prompt_template: The formatted prompt template (or string)
        input_variables: Variables to populate the template
        
    Returns:
        String response from LLM
    """
    if llm is None:
        raise ValueError("LLM not configured/provided")
    
    try:
        # Format prompt
        if hasattr(prompt_template, 'format'):
            formatted_prompt = prompt_template.format(**input_variables)
        else:
            formatted_prompt = str(prompt_template)
        
        # Invoke LLM
        if hasattr(llm, 'invoke'):
            response = llm.invoke(formatted_prompt)
            if hasattr(response, 'content'):
                return response.content.strip()
            return str(response).strip()
        else:
            # Fallback for simple callable
            return str(llm(formatted_prompt)).strip()
            
    except Exception as e:
        logger.error(f"LLM generation failed: {str(e)}")
        raise
