from src.config.database import get_db, Product, DemandScore
from src.models.agent_decisions import AgentDecision
from src.tools.demand_tools import (
    calculate_sales_velocity,
    calculate_demand_score,
    forecast_demand,
    analyze_demand_signals
)
from src.tools.inventory_tools import analyze_inventory_health
import logging
from datetime import datetime
import redis
import json
import os
from collections import defaultdict
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_demand_score(result):
    """
    Publish demand score to Redis for other agents to consume.
    Enhanced with comprehensive demand analysis.
    """
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        event = {
            "type": "demand_score",
            "agent": "DemandAnalysisAgent",
            "timestamp": datetime.now().isoformat(),
            "payload": result
        }
        
        redis_client.publish('demand_score', json.dumps(event, default=str))
        logger.info(f"[DemandAnalysisAgent] Published demand score: {result}")
        
    except Exception as e:
        logger.error(f"[DemandAnalysisAgent] Error publishing demand score: {e}")

def analyze_demand_score(db, product_id: str) -> Dict[str, Any]:
    """
    Analyze demand score for a product using comprehensive tools and analysis.
    Enhanced with reflection and reasoning capabilities.
    """
    try:
        logger.info(f"[DemandAnalysisAgent] Starting comprehensive demand analysis for product {product_id}")
        
        # Use demand tools for comprehensive analysis
        sales_velocity_data = calculate_sales_velocity(product_id, days=7)
        demand_score_data = calculate_demand_score(product_id)
        demand_forecast = forecast_demand(product_id, days_ahead=30)
        demand_signals = analyze_demand_signals(product_id)
        inventory_health = analyze_inventory_health(product_id)
        
        # Generate reasoning chain
        reasoning_chain = []
        reasoning_chain.append("Step 1: Analyzing sales velocity")
        if "error" not in sales_velocity_data:
            velocity = sales_velocity_data.get("sales_velocity", 0)
            reasoning_chain.append(f"Sales velocity: {velocity} units/day")
            if velocity > 10:
                reasoning_chain.append("High sales velocity indicates strong demand")
            elif velocity > 5:
                reasoning_chain.append("Moderate sales velocity indicates steady demand")
            else:
                reasoning_chain.append("Low sales velocity indicates weak demand")
        
        reasoning_chain.append("Step 2: Calculating demand score")
        if "error" not in demand_score_data:
            score = demand_score_data.get("demand_score", 0.5)
            reasoning_chain.append(f"Demand score: {score}")
            if score > 0.8:
                reasoning_chain.append("High demand score suggests strong market interest")
            elif score < 0.3:
                reasoning_chain.append("Low demand score suggests weak market interest")
            else:
                reasoning_chain.append("Moderate demand score suggests stable market interest")
        
        reasoning_chain.append("Step 3: Forecasting future demand")
        if "error" not in demand_forecast:
            avg_forecast = demand_forecast.get("avg_daily_forecast", 0)
            reasoning_chain.append(f"Forecasted daily demand: {avg_forecast} units")
        
        reasoning_chain.append("Step 4: Analyzing demand signals")
        if "error" not in demand_signals:
            sentiment = demand_signals.get("overall_sentiment", "neutral")
            reasoning_chain.append(f"Overall demand sentiment: {sentiment}")
        
        # Generate reflection on the analysis
        reflection = _generate_demand_reflection(
            sales_velocity_data, demand_score_data, demand_forecast, demand_signals, inventory_health
        )
        
        # Compile comprehensive results
        result = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat(),
            "sales_velocity_analysis": sales_velocity_data,
            "demand_score_analysis": demand_score_data,
            "demand_forecast": demand_forecast,
            "demand_signals": demand_signals,
            "inventory_health": inventory_health,
            "reasoning_chain": reasoning_chain,
            "reflection": reflection,
            "overall_demand_assessment": _generate_overall_assessment(
                sales_velocity_data, demand_score_data, demand_signals
            )
        }
        
        # Log agent decision with reflection
        agent_decision = AgentDecision(
            product_id=product_id,
            agent_name="DemandAnalysisAgent",
            decision_type="demand_analysis",
            input_data=json.dumps({"product_id": product_id}),
            output_data=json.dumps(result),
            confidence_score=0.9,
            explanation="Comprehensive demand analysis completed using multiple analytical tools",
            reflection=reflection,
            reasoning_chain=json.dumps(reasoning_chain),
            timestamp=datetime.now()
        )
        
        with next(get_db()) as db_session:
            db_session.add(agent_decision)
            db_session.commit()
        
        logger.info(f"[DemandAnalysisAgent] Completed demand analysis for product {product_id}")
        return result
        
    except Exception as e:
        logger.error(f"[DemandAnalysisAgent] Error in demand analysis: {e}")
        return {
            "error": str(e),
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        }

def _generate_demand_reflection(sales_velocity_data: dict, demand_score_data: dict, 
                              demand_forecast: dict, demand_signals: dict, 
                              inventory_health: dict) -> str:
    """
    Generate reflection on the demand analysis.
    """
    reflection_parts = []
    
    # Reflect on data quality
    data_quality_issues = []
    if "error" in sales_velocity_data:
        data_quality_issues.append("sales velocity data")
    if "error" in demand_score_data:
        data_quality_issues.append("demand score data")
    if "error" in demand_forecast:
        data_quality_issues.append("demand forecast data")
    
    if data_quality_issues:
        reflection_parts.append(f"Analysis limited by missing: {', '.join(data_quality_issues)}")
    else:
        reflection_parts.append("Analysis benefited from comprehensive data availability")
    
    # Reflect on demand strength
    if "error" not in demand_score_data:
        score = demand_score_data.get("demand_score", 0.5)
        if score > 0.8:
            reflection_parts.append("Strong demand signals detected, suggesting favorable market conditions")
        elif score < 0.3:
            reflection_parts.append("Weak demand signals detected, suggesting challenging market conditions")
        else:
            reflection_parts.append("Moderate demand signals detected, suggesting stable market conditions")
    
    # Reflect on inventory implications
    if "error" not in inventory_health:
        status = inventory_health.get("inventory_status", "unknown")
        if status == "out_of_stock":
            reflection_parts.append("Inventory out of stock - demand may be underestimated")
        elif status == "low_stock":
            reflection_parts.append("Low inventory levels - demand may be constrained by supply")
    
    # Reflect on forecasting confidence
    if "error" not in demand_forecast:
        confidence = demand_forecast.get("confidence", 0.5)
        if confidence > 0.8:
            reflection_parts.append("High confidence in demand forecasting due to consistent historical data")
        elif confidence < 0.5:
            reflection_parts.append("Low confidence in demand forecasting due to limited or inconsistent data")
    
    reflection_parts.append("Recommendation: Monitor demand patterns closely and adjust analysis as new data becomes available.")
    
    return " ".join(reflection_parts)

def _generate_overall_assessment(sales_velocity_data: dict, demand_score_data: dict, 
                               demand_signals: dict) -> dict:
    """
    Generate overall demand assessment based on all analyses.
    """
    assessment = {
        "demand_level": "moderate",
        "confidence": 0.7,
        "trend": "stable",
        "recommendations": []
    }
    
    # Assess demand level
    if "error" not in demand_score_data:
        score = demand_score_data.get("demand_score", 0.5)
        if score > 0.8:
            assessment["demand_level"] = "high"
        elif score < 0.3:
            assessment["demand_level"] = "low"
    
    # Assess trend
    if "error" not in demand_signals:
        sentiment = demand_signals.get("overall_sentiment", "neutral")
        if sentiment == "positive":
            assessment["trend"] = "increasing"
        elif sentiment == "negative":
            assessment["trend"] = "decreasing"
    
    # Generate recommendations
    if assessment["demand_level"] == "high":
        assessment["recommendations"].append("Consider price optimization to maximize revenue")
        assessment["recommendations"].append("Ensure adequate inventory to meet demand")
    elif assessment["demand_level"] == "low":
        assessment["recommendations"].append("Consider promotional activities to boost demand")
        assessment["recommendations"].append("Review pricing strategy for competitiveness")
    
    if assessment["trend"] == "increasing":
        assessment["recommendations"].append("Prepare for increased inventory needs")
    elif assessment["trend"] == "decreasing":
        assessment["recommendations"].append("Monitor closely for further decline")
    
    return assessment

def listen_for_feedback():
    """
    Listen for feedback messages on the 'feedback' Redis channel and log them.
    Enhanced with reflection on feedback.
    """
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )
    logger.info("[DemandAnalysisAgent] Listening for feedback on 'feedback' channel...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe('feedback')
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                feedback_data = json.loads(message['data'])
                logger.info(f"[DemandAnalysisAgent] Received feedback: {feedback_data}")
                
                # Reflect on feedback
                if feedback_data.get("agent") == "DemandAnalysisAgent":
                    reflection = _reflect_on_feedback(feedback_data)
                    logger.info(f"[DemandAnalysisAgent] Feedback reflection: {reflection}")
                    
    except KeyboardInterrupt:
        logger.info("[DemandAnalysisAgent] Stopping feedback listener...")
    finally:
        pubsub.unsubscribe()
        pubsub.close()

def _reflect_on_feedback(feedback_data: dict) -> str:
    """
    Reflect on received feedback to improve future analysis.
    """
    feedback_type = feedback_data.get("feedback_type", "general")
    message = feedback_data.get("message", "")
    
    reflection_parts = []
    
    if feedback_type == "accuracy":
        reflection_parts.append("Feedback on demand prediction accuracy received. Will review forecasting methodology.")
    elif feedback_type == "timeliness":
        reflection_parts.append("Feedback on analysis timeliness received. Will optimize processing speed.")
    elif feedback_type == "completeness":
        reflection_parts.append("Feedback on analysis completeness received. Will enhance data collection.")
    
    if "error" in message.lower() or "incorrect" in message.lower():
        reflection_parts.append("Negative feedback indicates need for methodology improvement.")
    elif "good" in message.lower() or "accurate" in message.lower():
        reflection_parts.append("Positive feedback validates current analytical approach.")
    
    reflection_parts.append("Will incorporate feedback into future demand analysis processes.")
    
    return " ".join(reflection_parts)

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        product_id = sys.argv[1]
        result = analyze_demand_score(None, product_id)
        print(json.dumps(result, indent=2))
    else:
        # Example usage
        result = analyze_demand_score(None, "P1001")
        print(json.dumps(result, indent=2))