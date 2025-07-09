from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.models.products import Product, InventoryLevel
from src.models.sales_data import SalesData
from src.config.database import get_db

logger = logging.getLogger(__name__)

def calculate_reorder_point(product_id: str) -> Dict[str, Any]:
    """
    Calculate optimal reorder point for a product based on sales velocity and lead time.
    """
    try:
        with next(get_db()) as db:
            # Get current inventory
            inventory = db.query(InventoryLevel).filter(
                InventoryLevel.product_id == product_id
            ).order_by(desc(InventoryLevel.last_updated)).first()
            
            if not inventory:
                return {"error": "No inventory data found for product"}
            
            # Calculate sales velocity (units per day)
            cutoff_date = datetime.now() - timedelta(days=30)
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).all()
            
            if not sales_data:
                return {
                    "error": "No sales data available for reorder point calculation",
                    "recommended_reorder_point": 10  # Default value
                }
            
            total_units = sum(sale.quantity_sold for sale in sales_data)
            daily_sales = total_units / 30
            
            # Assume 7 days lead time for reordering
            lead_time_days = 7
            safety_stock_days = 3  # 3 days of safety stock
            
            reorder_point = int(daily_sales * (lead_time_days + safety_stock_days))
            
            # Ensure minimum reorder point
            reorder_point = max(reorder_point, 5)
            
            return {
                "current_stock": inventory.stock_level,
                "daily_sales_rate": round(daily_sales, 2),
                "lead_time_days": lead_time_days,
                "safety_stock_days": safety_stock_days,
                "calculated_reorder_point": reorder_point,
                "current_reorder_point": inventory.reorder_point,
                "recommendation": "update" if abs(reorder_point - inventory.reorder_point) > 2 else "maintain",
                "confidence": 0.8
            }
            
    except Exception as e:
        logger.error(f"Error calculating reorder point for product {product_id}: {e}")
        return {"error": str(e)}

def analyze_inventory_health(product_id: str) -> Dict[str, Any]:
    """
    Analyze overall inventory health for a product.
    """
    try:
        with next(get_db()) as db:
            # Get current inventory
            inventory = db.query(InventoryLevel).filter(
                InventoryLevel.product_id == product_id
            ).order_by(desc(InventoryLevel.last_updated)).first()
            
            if not inventory:
                return {"error": "No inventory data found for product"}
            
            # Get product info
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"error": "Product not found"}
            
            # Calculate sales velocity
            cutoff_date = datetime.now() - timedelta(days=7)
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).all()
            
            daily_sales = sum(sale.quantity_sold for sale in sales_data) / 7 if sales_data else 0
            
            # Calculate days of inventory remaining
            days_remaining = inventory.stock_level / daily_sales if daily_sales > 0 else float('inf')
            
            # Determine inventory status
            if inventory.stock_level == 0:
                status = "out_of_stock"
                urgency = "critical"
            elif inventory.stock_level <= inventory.reorder_point:
                status = "low_stock"
                urgency = "high"
            elif days_remaining <= 7:
                status = "critical_low"
                urgency = "high"
            elif days_remaining <= 14:
                status = "moderate"
                urgency = "medium"
            else:
                status = "healthy"
                urgency = "low"
            
            # Calculate stock turnover rate
            monthly_sales = daily_sales * 30
            turnover_rate = monthly_sales / inventory.stock_level if inventory.stock_level > 0 else 0
            
            return {
                "product_id": product_id,
                "current_stock": inventory.stock_level,
                "reorder_point": inventory.reorder_point,
                "max_stock": inventory.max_stock,
                "daily_sales_rate": round(daily_sales, 2),
                "days_of_inventory_remaining": round(days_remaining, 1) if days_remaining != float('inf') else "infinite",
                "stock_turnover_rate": round(turnover_rate, 2),
                "inventory_status": status,
                "urgency_level": urgency,
                "recommendations": _generate_inventory_recommendations(status, inventory, daily_sales),
                "last_updated": inventory.last_updated.isoformat() if inventory.last_updated else None
            }
            
    except Exception as e:
        logger.error(f"Error analyzing inventory health for product {product_id}: {e}")
        return {"error": str(e)}

def _generate_inventory_recommendations(status: str, inventory: InventoryLevel, daily_sales: float) -> List[str]:
    """
    Generate inventory recommendations based on status.
    """
    recommendations = []
    
    if status == "out_of_stock":
        recommendations.append("Immediate restock required")
        recommendations.append("Consider expedited shipping")
    elif status == "low_stock":
        recommendations.append("Place reorder immediately")
        recommendations.append("Monitor sales closely")
    elif status == "critical_low":
        recommendations.append("Prepare for reorder")
        recommendations.append("Consider increasing reorder quantity")
    elif status == "moderate":
        recommendations.append("Monitor inventory levels")
        recommendations.append("Plan for next reorder cycle")
    else:  # healthy
        recommendations.append("Inventory levels are optimal")
        recommendations.append("Continue monitoring")
    
    return recommendations

def forecast_inventory_needs(product_id: str, days_ahead: int = 30) -> Dict[str, Any]:
    """
    Forecast inventory needs for a product over the next specified days.
    """
    try:
        with next(get_db()) as db:
            # Get current inventory
            inventory = db.query(InventoryLevel).filter(
                InventoryLevel.product_id == product_id
            ).order_by(desc(InventoryLevel.last_updated)).first()
            
            if not inventory:
                return {"error": "No inventory data found for product"}
            
            # Get historical sales for forecasting
            historical_days = max(days_ahead * 2, 60)
            cutoff_date = datetime.now() - timedelta(days=historical_days)
            
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).order_by(SalesData.sale_date.asc()).all()
            
            if len(sales_data) < 7:
                return {"error": "Insufficient sales data for forecasting"}
            
            # Calculate daily sales pattern
            daily_sales = {}
            for sale in sales_data:
                date_key = sale.sale_date.date()
                daily_sales[date_key] = daily_sales.get(date_key, 0) + sale.quantity_sold
            
            # Calculate average daily sales
            avg_daily_sales = sum(daily_sales.values()) / len(daily_sales)
            
            # Forecast inventory levels
            current_stock = inventory.stock_level
            forecast = []
            
            for day in range(days_ahead):
                forecast_date = datetime.now().date() + timedelta(days=day+1)
                projected_stock = max(0, current_stock - (avg_daily_sales * (day + 1)))
                
                forecast.append({
                    "date": forecast_date.isoformat(),
                    "projected_stock": round(projected_stock, 1),
                    "status": "out_of_stock" if projected_stock <= 0 else "low_stock" if projected_stock <= inventory.reorder_point else "healthy"
                })
            
            # Find when stock will run out
            stockout_day = None
            for i, day_forecast in enumerate(forecast):
                if day_forecast["projected_stock"] <= 0:
                    stockout_day = i + 1
                    break
            
            # Calculate recommended reorder quantity
            lead_time_days = 7
            safety_stock = avg_daily_sales * 3  # 3 days safety stock
            reorder_quantity = int(avg_daily_sales * (lead_time_days + days_ahead) + safety_stock)
            
            return {
                "product_id": product_id,
                "current_stock": current_stock,
                "avg_daily_sales": round(avg_daily_sales, 2),
                "forecast_period_days": days_ahead,
                "projected_stockout_day": stockout_day,
                "recommended_reorder_quantity": reorder_quantity,
                "forecast": forecast,
                "confidence": 0.7
            }
            
    except Exception as e:
        logger.error(f"Error forecasting inventory needs for product {product_id}: {e}")
        return {"error": str(e)}

def optimize_inventory_levels(product_id: str) -> Dict[str, Any]:
    """
    Provide inventory optimization recommendations.
    """
    try:
        # Get all inventory analyses
        health_analysis = analyze_inventory_health(product_id)
        reorder_analysis = calculate_reorder_point(product_id)
        forecast_analysis = forecast_inventory_needs(product_id, days_ahead=30)
        
        if "error" in health_analysis:
            return health_analysis
        
        # Combine insights for optimization
        optimization = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat(),
            "current_status": health_analysis["inventory_status"],
            "recommendations": {
                "immediate_actions": [],
                "short_term_actions": [],
                "long_term_actions": []
            },
            "metrics": {
                "current_stock": health_analysis["current_stock"],
                "reorder_point": health_analysis["reorder_point"],
                "stock_turnover": health_analysis["stock_turnover_rate"],
                "days_remaining": health_analysis["days_of_inventory_remaining"]
            }
        }
        
        # Generate optimization recommendations
        if health_analysis["urgency_level"] == "critical":
            optimization["recommendations"]["immediate_actions"].append("Emergency restock required")
        
        if health_analysis["urgency_level"] == "high":
            optimization["recommendations"]["immediate_actions"].append("Place reorder immediately")
        
        if "error" not in reorder_analysis and reorder_analysis["recommendation"] == "update":
            optimization["recommendations"]["short_term_actions"].append(f"Update reorder point to {reorder_analysis['calculated_reorder_point']}")
        
        if health_analysis["stock_turnover_rate"] < 0.5:
            optimization["recommendations"]["long_term_actions"].append("Consider reducing inventory levels - low turnover")
        elif health_analysis["stock_turnover_rate"] > 2.0:
            optimization["recommendations"]["long_term_actions"].append("Consider increasing inventory levels - high turnover")
        
        if "error" not in forecast_analysis and forecast_analysis.get("projected_stockout_day"):
            days_until_stockout = forecast_analysis["projected_stockout_day"]
            if days_until_stockout <= 7:
                optimization["recommendations"]["immediate_actions"].append(f"Stockout predicted in {days_until_stockout} days")
        
        return optimization
        
    except Exception as e:
        logger.error(f"Error optimizing inventory levels for product {product_id}: {e}")
        return {"error": str(e)} 