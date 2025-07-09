from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.products import Product
from src.models.competitor_prices import CompetitorPrice
from src.models.sales_data import SalesData
from src.models.price_history import PriceHistory
from src.config.database import get_db

logger = logging.getLogger(__name__)

def calculate_price_elasticity(product_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Calculate price elasticity of demand for a product based on historical data.
    """
    try:
        with next(get_db()) as db:
            # Get price history and sales data
            cutoff_date = datetime.now() - timedelta(days=days)
            
            price_history = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.timestamp >= cutoff_date
            ).order_by(PriceHistory.timestamp.asc()).all()
            
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).order_by(SalesData.sale_date.asc()).all()
            
            if len(price_history) < 2 or len(sales_data) < 2:
                return {
                    "elasticity": -1.0,  # Default elasticity
                    "confidence": 0.5,
                    "data_points": len(price_history),
                    "message": "Insufficient data for accurate elasticity calculation"
                }
            
            # Calculate elasticity using percentage changes
            price_changes = []
            quantity_changes = []
            
            for i in range(1, len(price_history)):
                price_change = (price_history[i].new_price - price_history[i-1].new_price) / price_history[i-1].new_price
                quantity_change = (sales_data[i].quantity_sold - sales_data[i-1].quantity_sold) / sales_data[i-1].quantity_sold if sales_data[i-1].quantity_sold > 0 else 0
                
                if price_change != 0:
                    price_changes.append(price_change)
                    quantity_changes.append(quantity_change)
            
            if not price_changes:
                return {
                    "elasticity": -1.0,
                    "confidence": 0.5,
                    "data_points": len(price_history),
                    "message": "No price changes detected in the period"
                }
            
            # Calculate average elasticity
            elasticities = [q/p for p, q in zip(price_changes, quantity_changes) if p != 0]
            avg_elasticity = sum(elasticities) / len(elasticities) if elasticities else -1.0
            
            return {
                "elasticity": round(avg_elasticity, 2),
                "confidence": min(0.9, len(elasticities) / 10),  # Higher confidence with more data points
                "data_points": len(price_history),
                "price_changes": len(price_changes),
                "message": "Elasticity calculated successfully"
            }
            
    except Exception as e:
        logger.error(f"Error calculating price elasticity for product {product_id}: {e}")
        return {
            "elasticity": -1.0,
            "confidence": 0.0,
            "error": str(e)
        }

def analyze_competitor_pricing(product_id: str) -> Dict[str, Any]:
    """
    Analyze competitor pricing for a product and provide insights.
    """
    try:
        with next(get_db()) as db:
            # Get current product info
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"error": "Product not found"}
            
            # Get recent competitor prices
            cutoff_date = datetime.now() - timedelta(days=7)
            competitor_prices = db.query(CompetitorPrice).filter(
                CompetitorPrice.product_id == product_id,
                CompetitorPrice.scraped_at >= cutoff_date
            ).all()
            
            if not competitor_prices:
                return {
                    "error": "No recent competitor data available",
                    "recommendation": "maintain_current_price"
                }
            
            # Calculate statistics
            prices = [cp.competitor_price for cp in competitor_prices]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            our_price = float(product.current_price or product.base_price)
            
            # Determine price position
            if our_price < min_price:
                position = "lowest"
                advantage = min_price - our_price
            elif our_price > max_price:
                position = "highest"
                advantage = our_price - max_price
            else:
                position = "competitive"
                advantage = 0
            
            # Generate recommendation
            if position == "lowest" and advantage > avg_price * 0.1:  # More than 10% below average
                recommendation = "consider_price_increase"
            elif position == "highest" and advantage > avg_price * 0.15:  # More than 15% above average
                recommendation = "consider_price_decrease"
            else:
                recommendation = "maintain_current_price"
            
            return {
                "our_price": our_price,
                "competitor_avg": round(avg_price, 2),
                "competitor_min": round(min_price, 2),
                "competitor_max": round(max_price, 2),
                "price_position": position,
                "price_advantage": round(advantage, 2),
                "recommendation": recommendation,
                "competitor_count": len(competitor_prices),
                "confidence": min(0.95, len(competitor_prices) / 5)  # Higher confidence with more competitors
            }
            
    except Exception as e:
        logger.error(f"Error analyzing competitor pricing for product {product_id}: {e}")
        return {"error": str(e)}

def calculate_optimal_price(product_id: str) -> Dict[str, Any]:
    """
    Calculate optimal price based on cost, demand, competition, and elasticity.
    """
    try:
        with next(get_db()) as db:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"error": "Product not found"}
            # Get current metrics
            cost_price = float(product.cost_price or 0)
            current_price = float(product.current_price or product.base_price)
            demand_score = float(product.demand_score or 0.5)
            elasticity = float(product.price_elasticity or -1.0)
            # Get competitor analysis
            competitor_analysis = analyze_competitor_pricing(product_id)
            if "error" in competitor_analysis:
                competitor_avg = float(current_price)
            else:
                competitor_avg = float(competitor_analysis["competitor_avg"])
            # Calculate optimal price using multiple factors
            # Factor 1: Cost-based pricing (minimum 20% margin)
            min_price = float(cost_price) * 1.2
            # Factor 2: Demand-based adjustment
            demand_adjustment = float(1.0 + (demand_score - 0.5) * 0.2)  # ±10% based on demand
            # Factor 3: Competition-based adjustment
            competition_ratio = float(competitor_avg) / float(current_price) if current_price > 0 else 1.0
            competition_adjustment = float(min(max(competition_ratio, 0.8), 1.2))  # Limit to ±20%
            # Factor 4: Elasticity-based adjustment
            if elasticity < -1.5:  # Very elastic (price sensitive)
                elasticity_adjustment = 0.95  # Slightly lower price
            elif elasticity > -0.5:  # Inelastic (less price sensitive)
                elasticity_adjustment = 1.05  # Slightly higher price
            else:
                elasticity_adjustment = 1.0
            elasticity_adjustment = float(elasticity_adjustment)
            # Calculate optimal price
            optimal_price = float(min_price) * float(demand_adjustment) * float(competition_adjustment) * float(elasticity_adjustment)
            # Ensure reasonable bounds
            optimal_price = max(optimal_price, min_price)
            optimal_price = min(optimal_price, competitor_avg * 1.5)  # Don't exceed 150% of competitor avg
            price_change = ((optimal_price - current_price) / current_price) * 100 if current_price > 0 else 0
            return {
                "current_price": round(float(current_price), 2),
                "optimal_price": round(float(optimal_price), 2),
                "price_change_percent": round(float(price_change), 1),
                "min_price": round(float(min_price), 2),
                "factors": {
                    "cost_based": round(float(min_price), 2),
                    "demand_adjustment": round(float(demand_adjustment), 3),
                    "competition_adjustment": round(float(competition_adjustment), 3),
                    "elasticity_adjustment": round(float(elasticity_adjustment), 3)
                },
                "recommendation": "increase" if price_change > 2 else "decrease" if price_change < -2 else "maintain",
                "confidence": 0.8
            }
    except Exception as e:
        logger.error(f"Error calculating optimal price for product {product_id}: {e}")
        return {"error": str(e)}

def get_pricing_recommendations(product_id: str) -> Dict[str, Any]:
    """
    Get comprehensive pricing recommendations for a product.
    """
    try:
        # Get all analyses
        elasticity_analysis = calculate_price_elasticity(product_id)
        competitor_analysis = analyze_competitor_pricing(product_id)
        optimal_price_analysis = calculate_optimal_price(product_id)
        
        # Combine insights
        recommendations = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat(),
            "elasticity_analysis": elasticity_analysis,
            "competitor_analysis": competitor_analysis,
            "optimal_price_analysis": optimal_price_analysis,
            "overall_recommendation": "maintain_current_price",
            "confidence": 0.7,
            "reasoning": []
        }
        
        # Determine overall recommendation
        if "error" not in optimal_price_analysis:
            rec = optimal_price_analysis["recommendation"]
            if rec == "increase":
                recommendations["overall_recommendation"] = "increase_price"
                recommendations["reasoning"].append("Optimal price analysis suggests price increase")
            elif rec == "decrease":
                recommendations["overall_recommendation"] = "decrease_price"
                recommendations["reasoning"].append("Optimal price analysis suggests price decrease")
        
        if "error" not in competitor_analysis:
            comp_rec = competitor_analysis["recommendation"]
            if comp_rec == "consider_price_increase":
                recommendations["reasoning"].append("Competitor analysis suggests potential price increase")
            elif comp_rec == "consider_price_decrease":
                recommendations["reasoning"].append("Competitor analysis suggests potential price decrease")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting pricing recommendations for product {product_id}: {e}")
        return {"error": str(e)} 