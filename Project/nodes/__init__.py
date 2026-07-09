# TODO: Import all node functions:
#   - data_analysis_node
#   - risk_assessment_node
#   - persona_node
#   - product_recommendation_node
#   - finalize_analysis_node
# TODO: Export all nodes in __all__ list

"""Node entrypoints for the Prospect Analysis workflow.

This module imports node callables from the sibling modules and exports them
for the workflow orchestrator. Missing node modules are tolerated at import
time so higher-level tools can still be inspected.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


def _safe_import(module_name: str, attr: str):
    try:
        module = __import__(f"Project.nodes.{module_name}", fromlist=[attr])
        return getattr(module, attr)
    except Exception:
        logger.debug("Node import failed: %s.%s", module_name, attr)
        return None


data_analysis_node = _safe_import("data_analysis_node", "data_analysis_node")
risk_assessment_node = _safe_import("risk_assessment_node", "risk_assessment_node")
persona_node = _safe_import("persona_node", "persona_node")
product_recommendation_node = _safe_import("product_recommendation_node", "product_recommendation_node")
finalize_analysis_node = _safe_import("finalize_analysis_node", "finalize_analysis_node")

__all__ = [
    "data_analysis_node",
    "risk_assessment_node",
    "persona_node",
    "product_recommendation_node",
    "finalize_analysis_node",
]

