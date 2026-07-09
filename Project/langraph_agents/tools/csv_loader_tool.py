import os
import pandas as pd
from typing import List, Dict, Any
from state import ProductRecommendation
from config import get_logger

logger = get_logger("tools.csv_loader_tool")

def load_products_csv(products_path: str) -> List[ProductRecommendation]:
    """Load products catalog from configured CSV file."""
    if not os.path.exists(products_path):
        logger.warning(f"Products CSV file not found at {products_path}")
        return []

    products = []
    try:
        df = pd.read_csv(products_path)
        for _, row in df.iterrows():
            products.append(
                ProductRecommendation(
                    product_id=str(row.get("product_id", "")),
                    product_name=str(row.get("product_name", "")),
                    product_type=str(row.get("product_type", "")),
                    suitability_score=0.0,
                    justification="",
                    risk_alignment=str(row.get("risk_alignment", "Moderate")),
                    expected_returns=str(row.get("expected_returns", "")),
                    fees=str(row.get("fees", "")),
                )
            )
    except Exception as e:
        logger.error(f"Error loading products from CSV: {e}")

    return products

def load_prospects_csv(prospects_path: str) -> List[Dict[str, Any]]:
    """Load prospects from configured CSV file."""
    if not os.path.exists(prospects_path):
        logger.warning(f"Prospects CSV file not found at {prospects_path}")
        return []

    try:
        df = pd.read_csv(prospects_path)
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error loading prospects from CSV: {e}")
        return []

def load_raw_products_csv(products_path: str) -> List[Dict[str, Any]]:
    """Load raw products from configured CSV file as dictionaries."""
    if not os.path.exists(products_path):
        logger.warning(f"Products CSV file not found at {products_path}")
        return []

    try:
        df = pd.read_csv(products_path)
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error loading raw products from CSV: {e}")
        return []

