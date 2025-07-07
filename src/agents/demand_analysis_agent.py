from src.config.database import get_sales_last_30_days, get_competitor_prices, get_stock_level
from src.config.llm import llm
from typing import List, Dict, Any
import datetime
import logging
import json

logger = logging.getLogger(__name__)


def analyze_demand_score(db, product_id: str) -> Dict[str, Any]:
    velocity = get_sales_last_30_days(db, product_id)
    competitor_prices = get_competitor_prices(db, product_id) * 100
    stock_level = get_stock_level(db, product_id)

    prompt = f"""
    You are a pricing & demand forecasting expert.

    INPUT
    ------
    • Sales Velocity (units / day): {velocity:.2f}
    • Competitor Price Advantage (%): {competitor_prices:.2f}
    (positive = we are cheaper than avg competitor)
    • Stock Level (units): {stock_level}

    TASK
    ----
    1. Produce a **single number** "demand_score" between 0.00 and 1.00 (float with 3 total digits, 2 after the decimal point, e.g. 0.87)
        (higher means stronger demand / urgency to restock or raise price).
    2. Give a one‑sentence "explanation".

    Respond ONLY in valid JSON:
    {{
        "demand_score": <float between 0.00 and 1.00, with 2 decimal places>,
        "explanation": "<string>"
    }}
    """.strip()

    try:
        content = llm.invoke(prompt)
        # Robustly extract the JSON string from the LLM response
        if hasattr(content, 'content'):
            content = content.content
        elif isinstance(content, dict) and 'content' in content:
            content = content['content']
        content = content.strip() if isinstance(content, str) else str(content)
        logger.error(f"LLM raw response: {content}")
        # Parse JSON response safely
        try:
            result = json.loads(content)
        except Exception as json_err:
            logger.error(f"Failed to parse LLM response as JSON: {json_err}")
            return {
                "product_id": product_id,
                "error": "LLM did not return valid JSON",
                "llm_raw_response": content
            }
        demand_score = round(float(result.get("demand_score", 0)), 2)

        # Update demand_signal in sales_data for this product
        from src.models.sales_data import SalesData
        db.query(SalesData).filter(SalesData.product_id == product_id).update({"demand_signal": demand_score})
        db.commit()

        return {
            "product_id": product_id,
            "sales_velocity": round(velocity, 2),
            "price_advantage_pct": round(competitor_prices * 100, 2),
            "stock_level": stock_level,
            "demand_score": demand_score,
            "llm_explanation": result.get("explanation", "No explanation provided."),
            "calculated_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"[Groq LLM] Error analyzing demand: {e}")
        return {
            "product_id": product_id,
            "error": "Failed to compute demand score using LLM",
            "details": str(e)
        }