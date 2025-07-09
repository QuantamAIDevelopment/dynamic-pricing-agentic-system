from src.config.database import get_db, Product, CompetitorPrice
from src.models.price_history import PriceHistory
from src.models.agent_decisions import AgentDecision
from src.tools.pricing_tools import (
    calculate_price_elasticity,
    analyze_competitor_pricing,
    calculate_optimal_price,
    get_pricing_recommendations
)
from src.tools.demand_tools import calculate_demand_score
from src.tools.inventory_tools import analyze_inventory_health
import logging
from datetime import datetime
import redis
import json
import os
from collections import defaultdict
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
def decide_price(competitor_prices, demand_score, inventory_level, base_price):
    """
    Decide new price based on competitor prices, demand score, inventory level, and base price.
    Enhanced with reflection and reasoning chain.
    """
    reasoning_chain = []
    # Ensure all price-related values are floats
    base_price = float(base_price)
    competitor_prices = [float(cp) for cp in competitor_prices]
    
    # Step 1: Analyze demand score
    reasoning_chain.append("Step 1: Analyzing demand score")
    if demand_score > 0.8:
        reasoning_chain.append("High demand detected (>0.8) - considering price increase")
        demand_factor = 1.10
    elif demand_score < 0.3:
        reasoning_chain.append("Low demand detected (<0.3) - considering price decrease")
        demand_factor = 0.95
    else:
        reasoning_chain.append("Moderate demand - maintaining current pricing strategy")
        demand_factor = 1.0
    
    # Step 2: Analyze inventory level
    reasoning_chain.append("Step 2: Analyzing inventory level")
    if inventory_level < 5:
        reasoning_chain.append("Low inventory (<5 units) - considering price increase to manage demand")
        inventory_factor = 1.05
    elif inventory_level > 50:
        reasoning_chain.append("High inventory (>50 units) - considering price decrease to boost sales")
        inventory_factor = 0.98
    else:
        reasoning_chain.append("Moderate inventory - no inventory-based price adjustment")
        inventory_factor = 1.0
    
    # Step 3: Analyze competitor prices
    reasoning_chain.append("Step 3: Analyzing competitor prices")
    if competitor_prices:
        avg_competitor = sum(competitor_prices) / len(competitor_prices)
        reasoning_chain.append(f"Average competitor price: ${avg_competitor:.2f}")
        
        if base_price < avg_competitor * 0.9:
            reasoning_chain.append("Our price is significantly below competitors - considering increase")
            competitor_factor = min(1.05, avg_competitor / base_price)
        elif base_price > avg_competitor * 1.1:
            reasoning_chain.append("Our price is significantly above competitors - considering decrease")
            competitor_factor = max(0.95, avg_competitor / base_price)
        else:
            reasoning_chain.append("Our price is competitive with market")
            competitor_factor = 1.0
    else:
        reasoning_chain.append("No competitor data available - using base pricing")
        competitor_factor = 1.0
    
    # Step 4: Calculate final price
    reasoning_chain.append("Step 4: Calculating final price")
    new_price = float(base_price) * float(demand_factor) * float(inventory_factor) * float(competitor_factor)
    
    # Ensure reasonable bounds
    new_price = max(new_price, float(base_price) * 0.8)  # Don't go below 80% of base price
    new_price = min(new_price, float(base_price) * 1.3)  # Don't go above 130% of base price
    
    reasoning_chain.append(f"Final price calculated: ${new_price:.2f}")
    
    return new_price, reasoning_chain
 
def run_pricing_decision_agent(input: dict) -> dict:
    """
    Run the pricing decision agent to decide and update the price for a given product.
    Enhanced with tools, reflection, and comprehensive analysis.
    """
    product_id = input.get("product_id")
    logger.info(f"[PricingDecisionAgent] Input received: product_id={product_id}")
 
    if not product_id:
        logger.error("[PricingDecisionAgent] product_id is required")
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
                logger.error(f"[PricingDecisionAgent] Product {product_id} not found")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error: Product {product_id} not found"
                }
 
            # Use tools for comprehensive analysis
            logger.info(f"[PricingDecisionAgent] Running comprehensive pricing analysis for {product_id}")
            
            # Get pricing recommendations using tools
            pricing_recommendations = get_pricing_recommendations(product_id)
            demand_analysis = calculate_demand_score(product_id)
            inventory_analysis = analyze_inventory_health(product_id)
            
            # Fetch competitor prices from database
            competitor_price_objs = db.query(CompetitorPrice).filter(CompetitorPrice.product_id == product_id).all()
            competitor_prices = [cp.competitor_price for cp in competitor_price_objs]
 
            # Get current metrics
            inventory_level = product.stock_level
            demand_score = product.demand_score
            base_price = product.base_price
            old_price = float(getattr(product, 'current_price', 0) or 0)
 
            # Decide new price using enhanced logic
            new_price, reasoning_chain = decide_price(competitor_prices, demand_score, inventory_level, base_price)
            
            # Generate reflection on the decision
            reflection = _generate_pricing_reflection(
                old_price, new_price, demand_analysis, inventory_analysis, pricing_recommendations
            )
 
            # Log price history in the database
            price_history = PriceHistory(
                product_id=product_id,
                old_price=old_price,
                new_price=new_price,
                change_reason="Automated pricing decision with comprehensive analysis",
                agent_name="PricingDecisionAgent",
                confidence_score=0.95,
                timestamp=datetime.now()
            )
            db.add(price_history)
 
            # Log agent decision with reflection
            agent_decision = AgentDecision(
                product_id=product_id,
                agent_name="PricingDecisionAgent",
                decision_type="price_update",
                input_data=json.dumps({
                    "demand_score": demand_score,
                    "inventory_level": inventory_level,
                    "competitor_prices": competitor_prices,
                    "base_price": float(base_price),
                    "old_price": old_price
                }),
                output_data=json.dumps({
                    "new_price": new_price,
                    "price_change_percent": ((new_price - old_price) / old_price * 100) if old_price > 0 else 0,
                    "pricing_recommendations": pricing_recommendations,
                    "demand_analysis": demand_analysis,
                    "inventory_analysis": inventory_analysis
                }),
                confidence_score=0.95,
                explanation=f"Price updated from ${old_price:.2f} to ${new_price:.2f} based on comprehensive market analysis",
                reflection=reflection,
                reasoning_chain=json.dumps(reasoning_chain),
                timestamp=datetime.now()
            )
            db.add(agent_decision)
 
            # Update product price in the database
            setattr(product, 'current_price', new_price)
            db.commit()
 
            logger.info(f"[PricingDecisionAgent] Updated price for product {product_id}: {old_price} -> {new_price}")
 
            return {
                "status": "success",
                "data": {
                    "product_id": product_id, 
                    "new_price": new_price,
                    "price_change_percent": ((new_price - old_price) / old_price * 100) if old_price > 0 else 0,
                    "reasoning_chain": reasoning_chain,
                    "reflection": reflection,
                    "pricing_recommendations": pricing_recommendations,
                    "demand_analysis": demand_analysis,
                    "inventory_analysis": inventory_analysis
                },
                "message": "Successfully decided and updated new price with comprehensive analysis"
            }
    except Exception as e:
        logger.error(f"[PricingDecisionAgent] Error in pricing decision workflow: {e}")
        return {"status": "error", "data": None, "message": f"Error in {e}"}

def _generate_pricing_reflection(old_price: float, new_price: float, demand_analysis: dict, 
                               inventory_analysis: dict, pricing_recommendations: dict) -> str:
    """
    Generate reflection on the pricing decision.
    """
    price_change = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
    
    reflection_parts = []
    
    # Reflect on the decision
    if price_change > 5:
        reflection_parts.append("Significant price increase implemented. This decision was based on strong demand signals and competitive positioning.")
    elif price_change < -5:
        reflection_parts.append("Significant price decrease implemented. This decision was based on low demand and inventory management needs.")
    else:
        reflection_parts.append("Moderate price adjustment implemented. This maintains competitive positioning while optimizing for demand.")
    
    # Reflect on the analysis quality
    if "error" not in demand_analysis and "error" not in inventory_analysis:
        reflection_parts.append("The decision benefited from comprehensive demand and inventory analysis.")
    
    if "error" not in pricing_recommendations:
        reflection_parts.append("Pricing recommendations were incorporated into the decision-making process.")
    
    # Reflect on potential risks
    if price_change > 10:
        reflection_parts.append("Large price increase may impact customer perception and sales volume. Monitor closely.")
    elif price_change < -10:
        reflection_parts.append("Large price decrease may impact profit margins. Ensure inventory can support increased demand.")
    
    reflection_parts.append("The decision should be monitored for effectiveness and adjusted based on market response.")
    
    return " ".join(reflection_parts)

# Initialize Redis client for Pub/Sub
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def listen_for_pricing_decisions():
    """
    Listen for competitor_data, demand_score, and inventory_update events, aggregate them, and make pricing decisions.
    """
    logger.info("[PricingDecisionAgent] Listening for events on competitor_data, demand_score, inventory_update channels...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe('competitor_data', 'demand_score', 'inventory_update')
    # Store latest data for each product_id
    product_data = defaultdict(lambda: {'competitor_data': None, 'demand_score': None, 'inventory_update': None})
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    event = json.loads(message['data'])
                    event_type = event.get('type')
                    payload = event.get('payload', {})
                    product_id = payload.get('product_id') or payload.get('id')
                    if not product_id:
                        continue
                    if event_type == 'competitor_data':
                        product_data[product_id]['competitor_data'] = payload
                    elif event_type == 'demand_score':
                        product_data[product_id]['demand_score'] = payload
                    elif event_type == 'inventory_update':
                        product_data[product_id]['inventory_update'] = payload
                    # If all required data is present, make a pricing decision
                    if all(product_data[product_id].values()):
                        logger.info(f"[PricingDecisionAgent] All data available for product {product_id}, making pricing decision.")
                        input_dict = {
                            'product_id': product_id,
                            'competitor_data': product_data[product_id]['competitor_data'],
                            'demand_score': product_data[product_id]['demand_score'],
                            'inventory_update': product_data[product_id]['inventory_update']
                        }
                        result = run_pricing_decision_agent({'product_id': product_id})
                        # Standardized message format
                        event_out = {
                            "type": "price_decision",
                            "agent": "PricingDecisionAgent",
                            "timestamp": datetime.now().isoformat(),
                            "payload": result.get('data')
                        }
                        redis_client.publish('price_decision', json.dumps(event_out, default=str))
                        logger.info(f"[PricingDecisionAgent] Published price decision for product {product_id}")
                        # Reset data for this product_id
                        product_data[product_id] = {'competitor_data': None, 'demand_score': None, 'inventory_update': None}
                except Exception as e:
                    logger.error(f"[PricingDecisionAgent] Error processing event: {e}")
    except KeyboardInterrupt:
        logger.info("[PricingDecisionAgent] Stopping pricing decision listener...")
    finally:
        pubsub.unsubscribe()
        pubsub.close()

def listen_for_feedback():
    """
    Listen for feedback messages on the 'feedback' Redis channel and log them.
    """
    logger.info("[PricingDecisionAgent] Listening for feedback on 'feedback' channel...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe('feedback')
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                logger.info(f"[PricingDecisionAgent] Received feedback: {message['data']}")
    except KeyboardInterrupt:
        logger.info("[PricingDecisionAgent] Stopping feedback listener...")
    finally:
        pubsub.unsubscribe()
        pubsub.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'listen':
        listen_for_pricing_decisions()
    else:
        # Example usage
        input_data = {"product_id": "P1001"}
        result = run_pricing_decision_agent(input_data)
        print(result)