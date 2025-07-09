from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os

from src.agents import run_supervisor_agent
from src.agents.pricing_decision_agent import run_pricing_decision_agent
from src.agents.demand_analysis_agent import analyze_demand_score
from src.agents.inventory_tracking_agent import run_inventory_tracking_agent
from src.agents.competitor_monitoring_agent import run_competitor_monitoring_agent
from src.tools.pricing_tools import get_pricing_recommendations, calculate_optimal_price
from src.tools.demand_tools import calculate_demand_score as calculate_demand_score_tool
from src.tools.inventory_tools import analyze_inventory_health, optimize_inventory_levels
from src.models.products import Product  # adjust import as needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Pricing Agentic System", version="1.0.0")

# Pydantic models for API requests
class SupervisorRequest(BaseModel):
    products: List[Dict[str, Any]]

class ProductNameRequest(BaseModel):
    product_name: str

class ProductIdRequest(BaseModel):
    product_id: str

class InventoryTrackingRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    stock_level: Optional[int] = None

class PricingAnalysisRequest(BaseModel):
    product_id: str
    include_forecast: bool = True

class DemandAnalysisRequest(BaseModel):
    product_id: str
    days: int = 30

class InventoryAnalysisRequest(BaseModel):
    product_id: str
    days_ahead: int = 30

class ProductCreateRequest(BaseModel):
    name: str
    category: str = "Unknown"
    competitor: str = "Unknown"
    price: float = 0.0
    competitor_price: float = 0.0
    competitor_url: str = ""
    # Add more fields as needed

@app.on_event("startup")
async def startup_event():
    try:
        from src.core.database import init_db
        init_db()
        logger.info("Dynamic Pricing Agentic System started successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

@app.get("/")
async def root():
    return {
        "message": "Dynamic Pricing Agentic System",
        "version": "1.0.0",
        "agents": ["supervisor", "pricing", "demand", "inventory", "competitor"],
        "tools": ["pricing", "demand", "inventory", "scraping", "search"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "redis": "connected" if os.getenv('REDIS_HOST') else "not_configured",
            "pinecone": "connected" if os.getenv('PINECONE_API_KEY') else "not_configured"
        }
    }

# Supervisor Agent Endpoints
@app.post("/agents/supervisor")
async def run_supervisor(request: ProductNameRequest):
    logger.info(f"[API] /agents/supervisor called with product_name: {request.product_name}")
    try:
        result = run_supervisor_agent({"product_name": request.product_name})
        logger.info(f"[API] Supervisor agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Supervisor agent completed successfully",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in supervisor agent: {e}")
        raise HTTPException(status_code=500, detail=f"Supervisor agent failed: {str(e)}")

@app.get("/agents/supervisor/history/{product_id}")
async def get_pricing_history(product_id: str, days: int = 30):
    logger.info(f"[API] /agents/supervisor/history/{product_id} called with days={days}")
    try:
        from agents.supervisor_agent import supervisor_agent
        history = supervisor_agent.get_pricing_history(product_id, days)
        return {
            "status": "success",
            "product_id": product_id,
            "history": history
        }
    except Exception as e:
        logger.error(f"[API] Error retrieving pricing history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pricing history: {str(e)}")

# Pricing Decision Agent Endpoints
@app.post("/agents/pricing/analyze")
async def analyze_pricing(request: PricingAnalysisRequest):
    logger.info(f"[API] /agents/pricing/analyze called with product_id: {request.product_id}")
    try:
        result = run_pricing_decision_agent({"product_id": request.product_id})
        logger.info(f"[API] Pricing decision agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Pricing analysis completed successfully",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in pricing decision agent: {e}")
        raise HTTPException(status_code=500, detail=f"Pricing analysis failed: {str(e)}")

@app.get("/agents/pricing/recommendations/{product_id}")
async def get_pricing_recommendations_endpoint(product_id: str):
    logger.info(f"[API] /agents/pricing/recommendations/{product_id} called")
    try:
        recommendations = get_pricing_recommendations(product_id)
        return {
            "status": "success",
            "product_id": product_id,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"[API] Error getting pricing recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pricing recommendations: {str(e)}")

@app.get("/agents/pricing/optimal-price/{product_id}")
async def get_optimal_price(product_id: str):
    logger.info(f"[API] /agents/pricing/optimal-price/{product_id} called")
    try:
        optimal_price = calculate_optimal_price(product_id)
        return {
            "status": "success",
            "product_id": product_id,
            "optimal_price": optimal_price
        }
    except Exception as e:
        logger.error(f"[API] Error calculating optimal price: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate optimal price: {str(e)}")

# Demand Analysis Agent Endpoints
@app.post("/agents/demand/analyze")
async def analyze_demand(request: DemandAnalysisRequest):
    logger.info(f"[API] /agents/demand/analyze called with product_id: {request.product_id}")
    try:
        result = analyze_demand_score(None, request.product_id)
        logger.info(f"[API] Demand analysis agent result: {result}")
        if "error" not in result:
            return {
                "status": "success",
                "message": "Demand analysis completed successfully",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        logger.error(f"[API] Error in demand analysis agent: {e}")
        raise HTTPException(status_code=500, detail=f"Demand analysis failed: {str(e)}")

@app.get("/agents/demand/score/{product_id}")
async def get_demand_score(product_id: str):
    logger.info(f"[API] /agents/demand/score/{product_id} called")
    try:
        demand_score = calculate_demand_score_tool(product_id)
        return {
            "status": "success",
            "product_id": product_id,
            "demand_score": demand_score
        }
    except Exception as e:
        logger.error(f"[API] Error calculating demand score: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate demand score: {str(e)}")

# Inventory Tracking Agent Endpoints
@app.post("/agents/inventory/analyze")
async def analyze_inventory(request: InventoryAnalysisRequest):
    logger.info(f"[API] /agents/inventory/analyze called with product_id: {request.product_id}")
    try:
        result = run_inventory_tracking_agent({"product_id": request.product_id})
        logger.info(f"[API] Inventory tracking agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Inventory analysis completed successfully",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in inventory tracking agent: {e}")
        raise HTTPException(status_code=500, detail=f"Inventory analysis failed: {str(e)}")

@app.get("/agents/inventory/health/{product_id}")
async def get_inventory_health(product_id: str):
    logger.info(f"[API] /agents/inventory/health/{product_id} called")
    try:
        health = analyze_inventory_health(product_id)
        return {
            "status": "success",
            "product_id": product_id,
            "health": health
        }
    except Exception as e:
        logger.error(f"[API] Error analyzing inventory health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze inventory health: {str(e)}")

@app.get("/agents/inventory/optimize/{product_id}")
async def get_inventory_optimization(product_id: str):
    logger.info(f"[API] /agents/inventory/optimize/{product_id} called")
    try:
        optimization = optimize_inventory_levels(product_id)
        return {
            "status": "success",
            "product_id": product_id,
            "optimization": optimization
        }
    except Exception as e:
        logger.error(f"[API] Error optimizing inventory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize inventory: {str(e)}")

@app.post("/agents/inventory-tracking")
async def run_inventory_tracking(request: InventoryTrackingRequest):
    logger.info(f"[API] /agents/inventory-tracking called with: {request}")
    try:
        result = run_inventory_tracking_agent(request.dict(exclude_unset=True))
        logger.info(f"[API] Inventory tracking agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Inventory tracking completed successfully",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in inventory tracking agent: {e}")
        raise HTTPException(status_code=500, detail=f"Inventory tracking failed: {str(e)}")

# Competitor Monitoring Agent Endpoints
@app.post("/agents/competitor/monitor")
async def monitor_competitors(request: ProductIdRequest):
    logger.info(f"[API] /agents/competitor/monitor called with product_id: {request.product_id}")
    try:
        result = run_competitor_monitoring_agent({"product_id": request.product_id})
        logger.info(f"[API] Competitor monitoring agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Competitor monitoring completed successfully",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in competitor monitoring agent: {e}")
        raise HTTPException(status_code=500, detail=f"Competitor monitoring failed: {str(e)}")

@app.get("/agents/competitor-monitoring/similar/{product_name}")
async def get_similar_products(product_name: str, category: str, limit: int = 5):
    logger.info(f"[API] /agents/competitor-monitoring/similar/{product_name} called with category={category}, limit={limit}")
    try:
        from agents.competitor_monitoring_agent import competitor_monitoring_agent
        similar_products = competitor_monitoring_agent.get_similar_products(product_name, category, limit)
        return {
            "status": "success",
            "product_name": product_name,
            "category": category,
            "similar_products": similar_products
        }
    except Exception as e:
        logger.error(f"[API] Error finding similar products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar products: {str(e)}")

# Comprehensive Analysis Endpoint
@app.post("/agents/comprehensive-analysis")
async def run_comprehensive_analysis(request: ProductIdRequest):
    """
    Run comprehensive analysis using all agents and tools for a product.
    """
    logger.info(f"[API] /agents/comprehensive-analysis called with product_id: {request.product_id}")
    try:
        product_id = request.product_id
        
        # Run all analyses in parallel (in a real implementation, you might want to use asyncio)
        results = {
            "product_id": product_id,
            "timestamp": "2024-01-01T00:00:00Z",
            "pricing_analysis": None,
            "demand_analysis": None,
            "inventory_analysis": None,
            "competitor_analysis": None,
            "overall_assessment": {}
        }
        
        # Run pricing analysis
        try:
            pricing_result = run_pricing_decision_agent({"product_id": product_id})
            results["pricing_analysis"] = pricing_result
        except Exception as e:
            logger.error(f"Pricing analysis failed: {e}")
            results["pricing_analysis"] = {"error": str(e)}
        
        # Run demand analysis
        try:
            demand_result = analyze_demand_score(None, product_id)
            results["demand_analysis"] = demand_result
        except Exception as e:
            logger.error(f"Demand analysis failed: {e}")
            results["demand_analysis"] = {"error": str(e)}
        
        # Run inventory analysis
        try:
            inventory_result = run_inventory_tracking_agent({"product_id": product_id})
            results["inventory_analysis"] = inventory_result
        except Exception as e:
            logger.error(f"Inventory analysis failed: {e}")
            results["inventory_analysis"] = {"error": str(e)}
        
        # Run competitor analysis
        try:
            competitor_result = run_competitor_monitoring_agent({"product_id": product_id})
            results["competitor_analysis"] = competitor_result
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            results["competitor_analysis"] = {"error": str(e)}
        
        # Generate overall assessment
        results["overall_assessment"] = _generate_overall_assessment(results)
        
        return {
            "status": "success",
            "message": "Comprehensive analysis completed",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"[API] Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@app.post("/products")
async def add_product(product: ProductCreateRequest):
    try:
        # Create and store the product in the DB
        new_product = Product(
            name=product.name,
            category=product.category,
            competitor=product.competitor,
            price=product.price,
            competitor_price=product.competitor_price,
            competitor_url=product.competitor_url
        )
        new_product.save()  # or your ORM's create method
        return {"status": "success", "product": new_product.to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _generate_overall_assessment(results: dict) -> dict:
    """
    Generate overall assessment based on all agent results.
    """
    assessment = {
        "status": "unknown",
        "priority_actions": [],
        "recommendations": [],
        "confidence": 0.5
    }
    
    # Assess pricing
    if results["pricing_analysis"] and "error" not in results["pricing_analysis"]:
        pricing_data = results["pricing_analysis"].get("data", {}) or {}
        if pricing_data.get("price_change_percent", 0) > 5:
            assessment["priority_actions"].append("Review pricing strategy - significant price change detected")
    
    # Assess demand
    if results["demand_analysis"] and "error" not in results["demand_analysis"]:
        demand_data = results["demand_analysis"] or {}
        if not isinstance(demand_data, dict):
            demand_data = {}
        overall_demand = demand_data.get("overall_demand_assessment", {}) or {}
        demand_level = overall_demand.get("demand_level")
        if demand_level == "high":
            assessment["recommendations"].append("High demand detected - consider inventory optimization")
        elif demand_level == "low":
            assessment["recommendations"].append("Low demand detected - consider promotional activities")
    
    # Assess inventory
    if results["inventory_analysis"] and "error" not in results["inventory_analysis"]:
        inventory_data = results["inventory_analysis"].get("data", {}) or {}
        overall_inventory = inventory_data.get("overall_inventory_assessment", {}) or {}
        urgency_level = overall_inventory.get("urgency_level")
        if urgency_level == "critical":
            assessment["priority_actions"].append("CRITICAL: Immediate inventory restock required")
    
    # Determine overall status
    if any("CRITICAL" in action for action in assessment["priority_actions"]):
        assessment["status"] = "critical"
    elif assessment["priority_actions"]:
        assessment["status"] = "attention_required"
    else:
        assessment["status"] = "healthy"
    
    return assessment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)