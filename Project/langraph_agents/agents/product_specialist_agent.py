


"""
Product Specialist Agent - Generate product recommendations.
"""

from typing import List, Dict, Any
from langraph_agents.base_agent import CriticalAgent
from state import WorkflowState, ProductRecommendation, ProspectData
from config import get_settings, get_gemini_model
from langraph_agents.tools.csv_loader_tool import load_raw_products_csv
from langraph_agents.tools.genai_tool import generate_llm_response 

class ProductSpecialistAgent(CriticalAgent):
    """Generate intelligent product recommendations."""
    
    def __init__(self, **kwargs):
        settings = get_settings()
        
        llm = get_gemini_model(model="gemini-2.5-flash-lite", temperature=settings.default_temperature)
        
        super().__init__(
            name="ProductSpecialistAgent",
            description="Generate product recommendations",
            llm=llm,
            **kwargs
        )
        
        self.products = self._load_products()
    
    def _load_products(self) -> List[Dict[str, Any]]:
        """Load product catalog."""
        settings = get_settings()
        products = load_raw_products_csv(settings.products_csv)
        if not products:
            self.logger.warning("Products list empty, using dummy data")
            return self._get_dummy_products()
        return products
    
    def _get_dummy_products(self) -> List[Dict[str, Any]]:
        """Dummy products for fallback."""
        return [
            {
                "product_id": "P001",
                "product_name": "Balanced Mutual Fund",
                "product_type": "Mutual Fund",
                "risk_level": "Moderate",
                "expected_returns": "8-10%",
                "fees": "1.5%",
                "min_investment": 5000
            },
            {
                "product_id": "P002",
                "product_name": "Fixed Deposit Ladder",
                "product_type": "Fixed Deposit",
                "risk_level": "Low",
                "expected_returns": "6-7%",
                "fees": "0%",
                "min_investment": 10000
            },
            {
                "product_id": "P003",
                "product_name": "Equity Index Fund",
                "product_type": "Index Fund",
                "risk_level": "High",
                "expected_returns": "10-12%",
                "fees": "0.5%",
                "min_investment": 5000
            },
            {
                "product_id": "P004",
                "product_name": "Debt Fund",
                "product_type": "Debt Fund",
                "risk_level": "Low",
                "expected_returns": "5-6%",
                "fees": "1.0%",
                "min_investment": 5000
            },
            {
                "product_id": "P005",
                "product_name": "Systematic Investment Plan",
                "product_type": "SIP",
                "risk_level": "Moderate",
                "expected_returns": "9-11%",
                "fees": "1.2%",
                "min_investment": 1000
            }
        ]
    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Generate product recommendations."""
        self.logger.info("Starting product recommendation")
        
        prospect_data = state.prospect.prospect_data
        risk_assessment = state.analysis.risk_assessment
        persona = state.analysis.persona_classification
        
        # Filter products
        filtered_products = self._filter_products(
            self.products,
            prospect_data,
            risk_assessment,
            persona
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(filtered_products, state)
        
        state.recommendations.recommended_products = recommendations
        
        self.logger.info(f"Generated {len(recommendations)} product recommendations")
        
        return state
    
    def _filter_products(
        self,
        products: List[Dict],
        prospect_data: ProspectData,
        risk_assessment: Any,
        persona: Any
    ) -> List[Dict]:
        """Filter products by suitability."""
        filtered = []
        
        # Risk level mapping
        risk_mapping = {
            "Low": ["Low"],
            "Moderate": ["Low", "Moderate"],
            "High": ["Low", "Moderate", "High"]
        }
        
        risk_level = risk_assessment.risk_level if risk_assessment else "Moderate"
        allowed_risks = risk_mapping.get(risk_level, ["Moderate"])
        
        # Max investment amount (80% of savings or 500K)
        max_investment = min(prospect_data.current_savings * 0.8, 500000)
        
        for product in products:
            # Check risk alignment
            product_risk = product.get("risk_level", "Moderate")
            if product_risk not in allowed_risks:
                continue
            
            # Check minimum investment
            min_inv = product.get("min_investment", 0)
            if min_inv > max_investment:
                continue
            
            filtered.append(product)
        
        return filtered
    
    async def _generate_recommendations(
        self,
        filtered_products: List[Dict],
        state: WorkflowState
    ) -> List[ProductRecommendation]:
        """Rank and select top products."""
        scored_products = []
        
        for product in filtered_products:
            score = self._calculate_suitability_score(product, state)
            scored_products.append((score, product))
        
        # Sort by score
        scored_products.sort(reverse=True, key=lambda x: x[0])
        
        # Select top 5
        recommendations = []
        for score, product in scored_products[:5]:
            justification = await self._generate_justification(product, state)
            
            rec = ProductRecommendation(
                product_id=product.get("product_id", ""),
                product_name=product.get("product_name", ""),
                product_type=product.get("product_type", ""),
                suitability_score=score,
                justification=justification,
                risk_alignment=self._get_risk_alignment(product, state),
                expected_returns=product.get("expected_returns", "N/A"),
                fees=product.get("fees", "N/A")
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_suitability_score(self, product: Dict, state: WorkflowState) -> float:
        """Calculate product suitability score."""
        score = 0.5  # Base score
        
        risk_assessment = state.analysis.risk_assessment
        persona = state.analysis.persona_classification
        
        # Risk alignment
        if risk_assessment:
            product_risk = product.get("risk_level", "Moderate")
            if product_risk == risk_assessment.risk_level:
                score += 0.3
            elif product_risk in ["Low", "Moderate"] and risk_assessment.risk_level == "Moderate":
                score += 0.2
        
        # Persona alignment
        if persona:
            if persona.persona_type == "Aggressive Growth" and product.get("risk_level") == "High":
                score += 0.15
            elif persona.persona_type == "Cautious Planner" and product.get("risk_level") == "Low":
                score += 0.15
            elif persona.persona_type == "Steady Saver":
                score += 0.1
        
        # Product type diversity bonus
        if product.get("product_type") in ["Mutual Fund", "SIP"]:
            score += 0.05
        
        return min(1.0, score)
    
    async def _generate_justification(self, product: Dict, state: WorkflowState) -> str:
        """Generate recommendation justification."""
        if self.llm:
            try:
                risk_level = state.analysis.risk_assessment.risk_level if state.analysis.risk_assessment else "Moderate"
                persona_type = state.analysis.persona_classification.persona_type if state.analysis.persona_classification else "Steady Saver"
                
                prompt = f"""Generate a brief justification (max 50 words) for recommending this product:
 
Product: {product.get('product_name')}
Type: {product.get('product_type')}
Returns: {product.get('expected_returns')}
Risk: {product.get('risk_level')}
 
Investor: {persona_type}, Risk Level: {risk_level}
 
Justification:"""
                
                response = generate_llm_response(self.llm, prompt, {})
                return response[:200]  # Limit length
                
            except Exception as e:
                self.logger.warning(f"AI justification failed: {e}")
        
        # Default justification
        return f"Suitable for {state.analysis.risk_assessment.risk_level if state.analysis.risk_assessment else 'Moderate'} risk profile with {product.get('expected_returns', 'competitive')} expected returns."
    
    def _get_risk_alignment(self, product: Dict, state: WorkflowState) -> str:
        """Get risk alignment statement."""
        product_risk = product.get("risk_level", "Moderate")
        investor_risk = state.analysis.risk_assessment.risk_level if state.analysis.risk_assessment else "Moderate"
        
        if product_risk == investor_risk:
            return "Perfect alignment with risk profile"
        elif product_risk == "Low" and investor_risk in ["Moderate", "High"]:
            return "Conservative option for stability"
        elif product_risk == "Moderate":
            return "Balanced option suitable for most investors"
        else:
            return "Consider as part of diversified portfolio"

