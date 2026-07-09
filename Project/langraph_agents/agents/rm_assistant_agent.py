
"""RM Assistant agent.

This agent answers user queries using workflow state as context. It uses the
BaseAgent's LLM helper when available, otherwise falls back to deterministic
rule-based answers derived from the analysis and recommendations stored in
the `WorkflowState`.
"""

from typing import Dict, Any, Optional, List
from config import get_settings, get_logger, get_gemini_model
from langraph_agents.base_agent import OptionalAgent
from state import WorkflowState
from langraph_agents.tools.genai_tool import generate_llm_response


class RMAssistantAgent(OptionalAgent):
	"""Assistant for relationship managers to answer queries using context."""

	def __init__(self, **kwargs):
		settings = get_settings()
		llm = get_gemini_model(model="gemini-2.5-flash-lite", temperature=settings.default_temperature)

		super().__init__(name="RMAssistantAgent", description="Assist RM with questions and context", llm=llm, **kwargs)
		self.logger = get_logger("agent.RMAssistantAgent")

	def retrieve_context(self, state: WorkflowState) -> Dict[str, Any]:
		"""Extract a compact context dictionary from the workflow state.

		This includes prospect summary, risk assessment, key product recommendations,
		and goal prediction if available.
		"""
		ctx: Dict[str, Any] = {}

		if state.prospect and state.prospect.prospect_data:
			p = state.prospect.prospect_data
			ctx["prospect"] = {
				"name": p.name,
				"age": p.age,
				"annual_income": p.annual_income,
				"current_savings": p.current_savings,
				"target_goal_amount": p.target_goal_amount,
				"investment_horizon_years": p.investment_horizon_years,
				"experience_level": p.investment_experience_level,
			}

		if state.analysis and state.analysis.risk_assessment:
			r = state.analysis.risk_assessment
			ctx["risk_assessment"] = {
				"risk_level": r.risk_level,
				"confidence": r.confidence_score,
				"risk_factors": r.risk_factors,
				"recommendations": r.recommendations,
			}

		if state.analysis and state.analysis.goal_prediction:
			g = state.analysis.goal_prediction
			ctx["goal_prediction"] = {
				"goal_success": g.goal_success,
				"probability": g.probability,
				"timeline": g.timeline_analysis,
			}

		# Top N product recommendations
		prods = state.recommendations.recommended_products or []
		ctx["top_products"] = [{"id": pr.product_id, "name": pr.product_name, "score": pr.suitability_score, "risk_alignment": pr.risk_alignment} for pr in prods[:5]]

		return ctx

	def process_query(self, query: str, context: Dict[str, Any]) -> str:
		"""Create a concise system prompt combining the query and extracted context.

		If LLM is not available, this method returns a deterministic answer using
		simple templates and context aggregation.
		"""
		# Build a short context summary
		lines: List[str] = []
		prospect = context.get("prospect")
		if prospect:
			lines.append(f"Prospect {prospect['name']}, age {prospect['age']}, income ₹{prospect['annual_income']:.0f}.")

		ra = context.get("risk_assessment")
		if ra:
			lines.append(f"Risk level: {ra['risk_level']} (conf {ra['confidence']:.2f}).")

		gp = context.get("goal_prediction")
		if gp:
			lines.append(f"Goal success probability: {gp['probability']:.0%} - {gp['goal_success']}")

		if context.get("top_products"):
			prod_names = ", ".join([p["name"] for p in context["top_products"] if p.get("name")])
			if prod_names:
				lines.append(f"Top products: {prod_names}")

		system_context = "\n".join(lines)

		prompt = f"You are a knowledgeable RM assistant. Use the context below to answer the user's question succinctly.\n\nCONTEXT:\n{system_context}\n\nQUESTION:\n{query}\n\nAnswer in 3-5 short bullet points or one short paragraph."

		# If no LLM, provide a simple template-based answer
		if self.llm is None:
			# Basic heuristic responses
			if "risk level" in system_context.lower() and "retire" in query.lower():
				return "Consider shifting to more conservative instruments and increasing allocation to debt and short-term debt funds; maintain an emergency buffer of 6-12 months."
			if "goal success probability" in system_context.lower() and "achieve" in query.lower():
				return "Probability indicates whether the plan is likely; consider increasing monthly savings or extending horizon to improve chances."
			# Generic fallback
			return "I reviewed the prospect context: update savings, diversify across equity/debt, and align product selection with stated risk tolerance."

		# Otherwise use LLM via generate_llm_response tool
		try:
			response = generate_llm_response(self.llm, prompt, {})
			return response
		except Exception as e:
			self.logger.error(f"LLM generation failed: {e}")
			return "I couldn't generate an AI response right now; please try again or rephrase the query."

	def format_response(self, raw: str) -> Dict[str, Any]:
		"""Return a structured response dict for chat UI."""
		return {"text": raw, "summary": raw.split('\n')[0] if raw else ""}

	async def execute(self, state: WorkflowState) -> WorkflowState:
		"""Main run method called by the workflow engine.

		Reads the current query from state.chat.current_query, generates a response,
		appends it to conversation_history and clears current_query.
		"""
		self.logger.info("RMAssistantAgent: executing chat response flow")

		query = state.chat.current_query
		if not query:
			self.logger.info("No current query found; nothing to do")
			return state

		context = self.retrieve_context(state)
		raw = self.process_query(query, context)
		formatted = self.format_response(raw)

		# Append to conversation history
		state.chat.conversation_history.append({"from": "user", "text": query})
		state.chat.conversation_history.append({"from": "assistant", "text": formatted["text"]})
		state.chat.response = formatted["text"]
		state.chat.current_query = None

		# Add a brief insight for RM
		state.key_insights.append("Assistant produced a short response to the last query.")

		return state


