from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.products import Product, DemandScore, InventoryLevel
from models.sales_data import SalesData
from config.database import get_db

logger = logging.getLogger(__name__)

def calculate_sales_velocity(product_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Calculate sales velocity (units sold per day) for a product.
    """
    try:
        with next(get_db()) as db:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get sales data for the period
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).all()
            
            if not sales_data:
                return {
                    "sales_velocity": 0.0,
                    "total_units_sold": 0,
                    "period_days": days,
                    "confidence": 0.0,
                    "message": "No sales data available for the period"
                }
            
            total_units = sum(sale.quantity_sold for sale in sales_data)
            sales_velocity = total_units / days
            
            # Calculate confidence based on data consistency
            daily_sales = {}
            for sale in sales_data:
                date_key = sale.sale_date.date()
                daily_sales[date_key] = daily_sales.get(date_key, 0) + sale.quantity_sold
            
            # Higher confidence if sales are consistent across days
            consistency_score = len(daily_sales) / days
            confidence = min(0.95, consistency_score)
            
            return {
                "sales_velocity": round(sales_velocity, 2),
                "total_units_sold": total_units,
                "period_days": days,
                "days_with_sales": len(daily_sales),
                "confidence": round(confidence, 2),
                "message": "Sales velocity calculated successfully"
            }
            
    except Exception as e:
        logger.error(f"Error calculating sales velocity for product {product_id}: {e}")
        return {
            "sales_velocity": 0.0,
            "confidence": 0.0,
            "error": str(e)
        }

def calculate_demand_score(product_id: str) -> Dict[str, Any]:
    """
    Calculate comprehensive demand score based on multiple factors.
    """
    try:
        with next(get_db()) as db:
            # Get product info
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"error": "Product not found"}
            
            # Get recent sales velocity
            velocity_data = calculate_sales_velocity(product_id, days=7)
            sales_velocity = velocity_data.get("sales_velocity", 0.0)
            
            # Get inventory level
            inventory = db.query(InventoryLevel).filter(
                InventoryLevel.product_id == product_id
            ).order_by(desc(InventoryLevel.last_updated)).first()
            
            current_stock = inventory.stock_level if inventory else 0
            reorder_point = inventory.reorder_point if inventory else 10
            
            # Calculate demand factors
            factors = {}
            
            # Factor 1: Sales velocity (0-1 score)
            if sales_velocity > 20:
                factors["sales_velocity_score"] = 1.0
            elif sales_velocity > 10:
                factors["sales_velocity_score"] = 0.8
            elif sales_velocity > 5:
                factors["sales_velocity_score"] = 0.6
            elif sales_velocity > 1:
                factors["sales_velocity_score"] = 0.4
            else:
                factors["sales_velocity_score"] = 0.2
            
            # Factor 2: Stock turnover (0-1 score)
            if current_stock == 0:
                factors["stock_turnover_score"] = 1.0  # High demand if out of stock
            elif current_stock <= reorder_point:
                factors["stock_turnover_score"] = 0.9  # Low stock indicates high demand
            elif current_stock <= reorder_point * 2:
                factors["stock_turnover_score"] = 0.7
            elif current_stock <= reorder_point * 3:
                factors["stock_turnover_score"] = 0.5
            else:
                factors["stock_turnover_score"] = 0.3  # High stock suggests lower demand
            
            # Factor 3: Recent sales trend (0-1 score)
            recent_velocity = calculate_sales_velocity(product_id, days=3)
            older_velocity = calculate_sales_velocity(product_id, days=7)
            
            if recent_velocity.get("sales_velocity", 0) > older_velocity.get("sales_velocity", 0):
                factors["trend_score"] = 0.9  # Increasing trend
            elif recent_velocity.get("sales_velocity", 0) == older_velocity.get("sales_velocity", 0):
                factors["trend_score"] = 0.7  # Stable trend
            else:
                factors["trend_score"] = 0.5  # Decreasing trend
            
            # Factor 4: Price elasticity impact
            elasticity = float(product.price_elasticity or -1.0)
            if elasticity < -1.5:
                factors["elasticity_score"] = 0.8  # Price sensitive, good for demand
            elif elasticity > -0.5:
                factors["elasticity_score"] = 0.6  # Less price sensitive
            else:
                factors["elasticity_score"] = 0.7  # Moderate elasticity
            
            # Calculate weighted demand score
            weights = {
                "sales_velocity_score": 0.4,
                "stock_turnover_score": 0.3,
                "trend_score": 0.2,
                "elasticity_score": 0.1
            }
            
            demand_score = sum(factors[key] * weights[key] for key in weights.keys())
            
            # Generate explanation
            explanation_parts = []
            if factors["sales_velocity_score"] > 0.7:
                explanation_parts.append("High sales velocity indicates strong demand")
            if factors["stock_turnover_score"] > 0.7:
                explanation_parts.append("Low stock levels suggest high demand")
            if factors["trend_score"] > 0.8:
                explanation_parts.append("Increasing sales trend")
            
            explanation = ". ".join(explanation_parts) if explanation_parts else "Moderate demand based on current metrics"
            
            return {
                "demand_score": round(demand_score, 2),
                "sales_velocity": round(sales_velocity, 2),
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "factors": factors,
                "explanation": explanation,
                "confidence": velocity_data.get("confidence", 0.5),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error calculating demand score for product {product_id}: {e}")
        return {"error": str(e)}

def forecast_demand(product_id: str, days_ahead: int = 30) -> Dict[str, Any]:
    """
    Forecast demand for a product over the next specified days.
    """
    try:
        with next(get_db()) as db:
            # Get historical sales data
            historical_days = max(days_ahead * 2, 60)  # Get at least 60 days of history
            cutoff_date = datetime.now() - timedelta(days=historical_days)
            
            sales_data = db.query(SalesData).filter(
                SalesData.product_id == product_id,
                SalesData.sale_date >= cutoff_date
            ).order_by(SalesData.sale_date.asc()).all()
            
            if len(sales_data) < 7:  # Need at least a week of data
                return {
                    "error": "Insufficient historical data for forecasting",
                    "min_required_days": 7,
                    "available_days": len(sales_data)
                }
            
            # Group sales by day
            daily_sales = {}
            for sale in sales_data:
                date_key = sale.sale_date.date()
                daily_sales[date_key] = daily_sales.get(date_key, 0) + sale.quantity_sold
            
            # Calculate moving average
            dates = sorted(daily_sales.keys())
            if len(dates) < 7:
                return {"error": "Insufficient daily data for forecasting"}
            
            # Simple moving average forecast
            recent_dates = dates[-7:]  # Last 7 days
            recent_sales = [daily_sales[date] for date in recent_dates]
            avg_daily_sales = sum(recent_sales) / len(recent_sales)
            
            # Calculate trend
            if len(recent_sales) >= 2:
                trend = (recent_sales[-1] - recent_sales[0]) / len(recent_sales)
            else:
                trend = 0
            
            # Forecast for each day
            forecast = []
            current_date = datetime.now().date()
            
            for i in range(days_ahead):
                forecast_date = current_date + timedelta(days=i+1)
                predicted_sales = max(0, avg_daily_sales + (trend * i))
                forecast.append({
                    "date": forecast_date.isoformat(),
                    "predicted_sales": round(predicted_sales, 1),
                    "confidence": max(0.3, 1.0 - (i * 0.02))  # Decreasing confidence over time
                })
            
            total_forecast = sum(day["predicted_sales"] for day in forecast)
            
            return {
                "product_id": product_id,
                "forecast_period_days": days_ahead,
                "total_forecasted_sales": round(total_forecast, 1),
                "avg_daily_forecast": round(total_forecast / days_ahead, 1),
                "trend": round(trend, 2),
                "forecast": forecast,
                "confidence": 0.7,
                "method": "moving_average",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error forecasting demand for product {product_id}: {e}")
        return {"error": str(e)}

def analyze_demand_signals(product_id: str) -> Dict[str, Any]:
    """
    Analyze various demand signals for a product.
    """
    try:
        # Get all demand-related data
        demand_score_data = calculate_demand_score(product_id)
        velocity_data = calculate_sales_velocity(product_id, days=7)
        forecast_data = forecast_demand(product_id, days_ahead=7)
        
        # Combine signals
        signals = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat(),
            "demand_score": demand_score_data.get("demand_score", 0.5),
            "sales_velocity": velocity_data.get("sales_velocity", 0.0),
            "short_term_forecast": forecast_data.get("avg_daily_forecast", 0.0),
            "signals": [],
            "overall_sentiment": "neutral"
        }
        
        # Analyze individual signals
        if demand_score_data.get("demand_score", 0) > 0.8:
            signals["signals"].append("high_demand_score")
        elif demand_score_data.get("demand_score", 0) < 0.3:
            signals["signals"].append("low_demand_score")
        
        if velocity_data.get("sales_velocity", 0) > 10:
            signals["signals"].append("high_sales_velocity")
        elif velocity_data.get("sales_velocity", 0) < 1:
            signals["signals"].append("low_sales_velocity")
        
        if forecast_data.get("trend", 0) > 0.5:
            signals["signals"].append("increasing_trend")
        elif forecast_data.get("trend", 0) < -0.5:
            signals["signals"].append("decreasing_trend")
        
        # Determine overall sentiment
        positive_signals = sum(1 for signal in signals["signals"] if "high" in signal or "increasing" in signal)
        negative_signals = sum(1 for signal in signals["signals"] if "low" in signal or "decreasing" in signal)
        
        if positive_signals > negative_signals:
            signals["overall_sentiment"] = "positive"
        elif negative_signals > positive_signals:
            signals["overall_sentiment"] = "negative"
        else:
            signals["overall_sentiment"] = "neutral"
        
        return signals
        
    except Exception as e:
        logger.error(f"Error analyzing demand signals for product {product_id}: {e}")
        return {"error": str(e)} 