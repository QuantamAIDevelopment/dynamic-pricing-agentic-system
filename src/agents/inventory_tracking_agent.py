import logging
from datetime import datetime
import json
from src.config.database import get_db, Product, InventoryLevel
from src.models.agent_decisions import AgentDecision
from src.tools.inventory_tools import (
    calculate_reorder_point,
    analyze_inventory_health,
    forecast_inventory_needs,
    optimize_inventory_levels
)
from src.tools.demand_tools import calculate_sales_velocity
import redis
import os
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_inventory_update(data):
    """
    Publish inventory update to Redis for other agents to consume.
    Enhanced with comprehensive inventory analysis.
    """
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        event = {
            "type": "inventory_update",
            "agent": "InventoryTrackingAgent",
            "timestamp": datetime.now().isoformat(),
            "payload": data
        }
        
        redis_client.publish('inventory_update', json.dumps(event, default=str))
        logger.info(f"[InventoryTrackingAgent] Published inventory update: {data}")
        
    except Exception as e:
        logger.error(f"[InventoryTrackingAgent] Error publishing inventory update: {e}")

def listen_for_feedback():
    """
    Listen for feedback messages on the 'feedback' Redis channel and log them.
    Enhanced with reflection on feedback.
    """
    logger.info("[InventoryTrackingAgent] Listening for feedback on 'feedback' channel...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe('feedback')
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                feedback_data = json.loads(message['data'])
                logger.info(f"[InventoryTrackingAgent] Received feedback: {feedback_data}")
                
                # Reflect on feedback
                if feedback_data.get("agent") == "InventoryTrackingAgent":
                    reflection = _reflect_on_feedback(feedback_data)
                    logger.info(f"[InventoryTrackingAgent] Feedback reflection: {reflection}")
                    
    except KeyboardInterrupt:
        logger.info("[InventoryTrackingAgent] Stopping feedback listener...")
    finally:
        pubsub.unsubscribe()
        pubsub.close()

def _reflect_on_feedback(feedback_data: dict) -> str:
    """
    Reflect on received feedback to improve future inventory tracking.
    """
    feedback_type = feedback_data.get("feedback_type", "general")
    message = feedback_data.get("message", "")
    
    reflection_parts = []
    
    if feedback_type == "accuracy":
        reflection_parts.append("Feedback on inventory level accuracy received. Will review tracking methodology.")
    elif feedback_type == "timeliness":
        reflection_parts.append("Feedback on inventory update timeliness received. Will optimize update frequency.")
    elif feedback_type == "completeness":
        reflection_parts.append("Feedback on inventory analysis completeness received. Will enhance monitoring coverage.")
    
    if "error" in message.lower() or "incorrect" in message.lower():
        reflection_parts.append("Negative feedback indicates need for inventory tracking improvement.")
    elif "good" in message.lower() or "accurate" in message.lower():
        reflection_parts.append("Positive feedback validates current inventory tracking approach.")
    
    reflection_parts.append("Will incorporate feedback into future inventory tracking processes.")
    
    return " ".join(reflection_parts)

def run_inventory_tracking_agent(input: dict) -> dict:
    """
    Run the inventory tracking agent to monitor and analyze inventory levels.
    Enhanced with tools, reflection, and comprehensive analysis.
    """
    product_id = input.get("product_id")
    logger.info(f"[InventoryTrackingAgent] Input received: product_id={product_id}")
 
    if not product_id:
        logger.error("[InventoryTrackingAgent] product_id is required")
        return {
            "status": "error",
            "data": None,
            "message": "Error: product_id is required"
        }
 
    try:
        with next(get_db()) as db:
            # Fetch product info from database
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                logger.error(f"[InventoryTrackingAgent] Product {product_id} not found")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error: Product {product_id} not found"
                }
 
            # Use inventory tools for comprehensive analysis
            logger.info(f"[InventoryTrackingAgent] Running comprehensive inventory analysis for {product_id}")
            
            # Get inventory analyses using tools
            inventory_health = analyze_inventory_health(product_id)
            reorder_analysis = calculate_reorder_point(product_id)
            inventory_forecast = forecast_inventory_needs(product_id, days_ahead=30)
            inventory_optimization = optimize_inventory_levels(product_id)
            sales_velocity = calculate_sales_velocity(product_id, days=7)
            
            # Generate reasoning chain
            reasoning_chain = []
            reasoning_chain.append("Step 1: Analyzing current inventory health")
            if "error" not in inventory_health:
                status = inventory_health.get("inventory_status", "unknown")
                reasoning_chain.append(f"Inventory status: {status}")
                if status == "out_of_stock":
                    reasoning_chain.append("Critical: Product is out of stock")
                elif status == "low_stock":
                    reasoning_chain.append("Warning: Inventory levels are low")
                elif status == "healthy":
                    reasoning_chain.append("Inventory levels are healthy")
            
            reasoning_chain.append("Step 2: Calculating reorder point")
            if "error" not in reorder_analysis:
                current_rp = reorder_analysis.get("current_reorder_point", 0)
                calculated_rp = reorder_analysis.get("calculated_reorder_point", 0)
                reasoning_chain.append(f"Current reorder point: {current_rp}, Calculated: {calculated_rp}")
                if reorder_analysis.get("recommendation") == "update":
                    reasoning_chain.append("Recommendation: Update reorder point based on sales velocity")
            
            reasoning_chain.append("Step 3: Forecasting inventory needs")
            if "error" not in inventory_forecast:
                stockout_day = inventory_forecast.get("projected_stockout_day")
                if stockout_day:
                    reasoning_chain.append(f"Projected stockout in {stockout_day} days")
                else:
                    reasoning_chain.append("No stockout projected in forecast period")
            
            reasoning_chain.append("Step 4: Analyzing sales velocity")
            if "error" not in sales_velocity:
                velocity = sales_velocity.get("sales_velocity", 0)
                reasoning_chain.append(f"Sales velocity: {velocity} units/day")
            
            # Generate reflection on the analysis
            reflection = _generate_inventory_reflection(
                inventory_health, reorder_analysis, inventory_forecast, inventory_optimization, sales_velocity
            )
            
            # Compile comprehensive results
            result = {
                "product_id": product_id,
                "timestamp": datetime.now().isoformat(),
                "inventory_health": inventory_health,
                "reorder_analysis": reorder_analysis,
                "inventory_forecast": inventory_forecast,
                "inventory_optimization": inventory_optimization,
                "sales_velocity": sales_velocity,
                "reasoning_chain": reasoning_chain,
                "reflection": reflection,
                "overall_inventory_assessment": _generate_overall_inventory_assessment(
                    inventory_health, reorder_analysis, inventory_forecast
                )
            }
            
            # Log agent decision with reflection
            agent_decision = AgentDecision(
                product_id=product_id,
                agent_name="InventoryTrackingAgent",
                decision_type="inventory_analysis",
                input_data=json.dumps({"product_id": product_id}),
                output_data=json.dumps(result),
                confidence_score=0.9,
                explanation="Comprehensive inventory analysis completed using multiple analytical tools",
                reflection=reflection,
                reasoning_chain=json.dumps(reasoning_chain),
                timestamp=datetime.now()
            )
            db.add(agent_decision)
            
            # Update product stock level if inventory health analysis is available
            if "error" not in inventory_health:
                current_stock = inventory_health.get("current_stock", product.stock_level)
                if current_stock != product.stock_level:
                    product.stock_level = current_stock
                    product.last_updated = datetime.now()
                    logger.info(f"[InventoryTrackingAgent] Updated stock level for product {product_id}: {current_stock}")
            
            db.commit()
 
            logger.info(f"[InventoryTrackingAgent] Completed inventory analysis for product {product_id}")
 
            return {
                "status": "success",
                "data": result,
                "message": "Successfully completed comprehensive inventory analysis"
            }
    except Exception as e:
        logger.error(f"[InventoryTrackingAgent] Error in inventory tracking workflow: {e}")
        return {"status": "error", "data": None, "message": f"Error in {e}"}

def _generate_inventory_reflection(inventory_health: dict, reorder_analysis: dict, 
                                 inventory_forecast: dict, inventory_optimization: dict,
                                 sales_velocity: dict) -> str:
    """
    Generate reflection on the inventory analysis.
    """
    reflection_parts = []
    
    # Reflect on data quality
    data_quality_issues = []
    if "error" in inventory_health:
        data_quality_issues.append("inventory health data")
    if "error" in reorder_analysis:
        data_quality_issues.append("reorder point data")
    if "error" in inventory_forecast:
        data_quality_issues.append("inventory forecast data")
    
    if data_quality_issues:
        reflection_parts.append(f"Analysis limited by missing: {', '.join(data_quality_issues)}")
    else:
        reflection_parts.append("Analysis benefited from comprehensive inventory data availability")
    
    # Reflect on inventory status
    if "error" not in inventory_health:
        status = inventory_health.get("inventory_status", "unknown")
        if status == "out_of_stock":
            reflection_parts.append("Critical inventory situation detected - immediate action required")
        elif status == "low_stock":
            reflection_parts.append("Low inventory levels detected - reorder planning needed")
        elif status == "healthy":
            reflection_parts.append("Inventory levels are healthy and well-managed")
    
    # Reflect on reorder point optimization
    if "error" not in reorder_analysis:
        if reorder_analysis.get("recommendation") == "update":
            reflection_parts.append("Reorder point optimization recommended based on current sales patterns")
    
    # Reflect on forecasting insights
    if "error" not in inventory_forecast:
        stockout_day = inventory_forecast.get("projected_stockout_day")
        if stockout_day and stockout_day <= 7:
            reflection_parts.append("Imminent stockout predicted - urgent reorder required")
        elif stockout_day and stockout_day <= 14:
            reflection_parts.append("Stockout predicted in near future - proactive reorder recommended")
    
    # Reflect on sales velocity impact
    if "error" not in sales_velocity:
        velocity = sales_velocity.get("sales_velocity", 0)
        if velocity > 10:
            reflection_parts.append("High sales velocity indicates need for frequent inventory monitoring")
        elif velocity < 1:
            reflection_parts.append("Low sales velocity suggests inventory may be overstocked")
    
    reflection_parts.append("Recommendation: Continue monitoring inventory levels and adjust reorder strategies based on sales patterns.")
    
    return " ".join(reflection_parts)

def _generate_overall_inventory_assessment(inventory_health: dict, reorder_analysis: dict, 
                                         inventory_forecast: dict) -> dict:
    """
    Generate overall inventory assessment based on all analyses.
    """
    assessment = {
        "inventory_status": "unknown",
        "urgency_level": "low",
        "confidence": 0.7,
        "recommendations": []
    }
    
    # Assess inventory status
    if "error" not in inventory_health:
        status = inventory_health.get("inventory_status", "unknown")
        assessment["inventory_status"] = status
        
        if status == "out_of_stock":
            assessment["urgency_level"] = "critical"
        elif status == "low_stock":
            assessment["urgency_level"] = "high"
        elif status == "critical_low":
            assessment["urgency_level"] = "high"
        elif status == "moderate":
            assessment["urgency_level"] = "medium"
        else:
            assessment["urgency_level"] = "low"
    
    # Generate recommendations
    if assessment["urgency_level"] == "critical":
        assessment["recommendations"].append("Immediate restock required")
        assessment["recommendations"].append("Consider expedited shipping")
    elif assessment["urgency_level"] == "high":
        assessment["recommendations"].append("Place reorder immediately")
        assessment["recommendations"].append("Monitor sales closely")
    elif assessment["urgency_level"] == "medium":
        assessment["recommendations"].append("Prepare for reorder")
        assessment["recommendations"].append("Monitor inventory levels")
    else:
        assessment["recommendations"].append("Continue monitoring")
        assessment["recommendations"].append("Maintain current inventory levels")
    
    # Add reorder point recommendations
    if "error" not in reorder_analysis and reorder_analysis.get("recommendation") == "update":
        assessment["recommendations"].append("Update reorder point based on sales velocity")
    
    # Add forecasting recommendations
    if "error" not in inventory_forecast:
        stockout_day = inventory_forecast.get("projected_stockout_day")
        if stockout_day and stockout_day <= 7:
            assessment["recommendations"].append("Urgent reorder needed to prevent stockout")
        elif stockout_day and stockout_day <= 14:
            assessment["recommendations"].append("Plan reorder to prevent future stockout")
    
    return assessment

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
        result = run_inventory_tracking_agent({"product_id": product_id})
        print(json.dumps(result, indent=2))
    else:
        # Example usage
        input_data = {"product_id": "P1001"}
        result = run_inventory_tracking_agent(input_data)
        print(json.dumps(result, indent=2)) 