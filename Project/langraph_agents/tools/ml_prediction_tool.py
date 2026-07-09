from typing import Tuple, Dict, Any
from ml.training.predict_risk_profile import predict_risk_profile
from ml.training.predict_goal_success import predict_goal_success

async def predict_risk_profile_tool(prospect_features: dict) -> Tuple[str, float]:
    """
    Predict risk profile using the ML prediction function.
    
    Args:
        prospect_features: Dictionary containing prospect characteristics
        
    Returns:
        Tuple of (risk_level, confidence_score)
    """
    return await predict_risk_profile(prospect_features)

async def predict_goal_success_tool(goal_data: dict) -> Dict[str, Any]:
    """
    Predict goal success using the ML prediction function.
    
    Args:
        goal_data: Dictionary containing goal parameters
        
    Returns:
        Dictionary containing success likelihood and probability
    """
    return await predict_goal_success(goal_data)
