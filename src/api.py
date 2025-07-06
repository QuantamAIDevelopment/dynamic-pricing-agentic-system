from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os

from agents import run_supervisor_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Pricing Agentic System", version="1.0.0")

# Pydantic models for API requests
class SupervisorRequest(BaseModel):
    products: List[Dict[str, Any]]

class ProductNameRequest(BaseModel):
    product_name: str

@app.on_event("startup")
async def startup_event():
    try:
        from core.database import init_db
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
        "agents": ["supervisor"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)