from typing import Dict, Any
from state import ProspectData

def validate_prospect_data(prospect_data: ProspectData) -> Dict[str, Any]:
    """
    Comprehensive data validation for prospect.
    
    Args:
        prospect_data: Prospect information
        
    Returns:
        Dictionary with validation results (errors, missing_fields, quality_score)
    """
    errors = []
    missing_fields = []
    quality_score = 1.0
    
    # Check required fields
    required_fields = [
        'prospect_id', 'name', 'age', 'annual_income',
        'current_savings', 'target_goal_amount',
        'investment_horizon_years', 'number_of_dependents',
        'investment_experience_level'
    ]
    
    for field in required_fields:
        value = getattr(prospect_data, field, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field)
            quality_score -= 0.1
    
    # Validate age range
    if prospect_data.age is not None:
        if prospect_data.age < 18 or prospect_data.age > 100:
            errors.append(f"Age {prospect_data.age} is outside valid range (18-100)")
            quality_score -= 0.15
    
    # Validate income
    if prospect_data.annual_income is not None:
        if prospect_data.annual_income < 50000:
            errors.append(f"Annual income {prospect_data.annual_income} below minimum threshold")
            quality_score -= 0.1
    
    # Validate savings vs goal
    if prospect_data.current_savings is not None and prospect_data.target_goal_amount is not None:
        if prospect_data.current_savings > prospect_data.target_goal_amount:
            errors.append("Current savings exceed target goal")
            quality_score -= 0.05
    
    # Validate investment horizon
    if prospect_data.investment_horizon_years is not None:
        if prospect_data.investment_horizon_years < 1:
            errors.append("Investment horizon must be at least 1 year")
            quality_score -= 0.1
    
    # Validate experience level
    valid_experience_levels = ["Beginner", "Intermediate", "Advanced"]
    if prospect_data.investment_experience_level not in valid_experience_levels:
        errors.append(f"Invalid experience level: {prospect_data.investment_experience_level}")
        quality_score -= 0.1
    
    # Ensure quality score is between 0 and 1
    quality_score = max(0.0, min(1.0, quality_score))
    
    return {
        "errors": errors,
        "missing_fields": missing_fields,
        "quality_score": quality_score
    }
