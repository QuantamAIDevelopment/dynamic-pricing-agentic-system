from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from core.database import init_db
import logging
import os

from agents import run_web_scraping_agent, run_competitor_monitoring_agent, run_supervisor_agent

logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Pricing Agentic System", version="1.0.0")

# Pydantic models for API requests
class WebScrapingRequest(BaseModel):
    domain: str
    category: str
    product_name: Optional[str] = None

class CompetitorMonitoringRequest(BaseModel):
    product_data: Optional[Dict[str, Any]] = None

class SupervisorRequest(BaseModel):
    products: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    try:
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
        "agents": ["web_scraping", "competitor_monitoring", "supervisor"]
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

@app.post("/agents/web-scraping")
async def run_web_scraping(request: WebScrapingRequest):
    logger.warning("[API] Direct web scraping agent call detected. For full agentic workflow, use /agents/supervisor.")
    logger.info(f"[API] /agents/web-scraping called with: {request}")
    try:
        result = run_web_scraping_agent({
            "domain": request.domain,
            "category": request.category,
            "product_name": request.product_name
        })
        logger.info(f"[API] Web scraping agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Web scraping completed successfully (note: for full agentic workflow, use /agents/supervisor)",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in web scraping agent: {e}")
        raise HTTPException(status_code=500, detail=f"Web scraping failed: {str(e)}")

@app.post("/agents/competitor-monitoring")
async def run_competitor_monitoring(request: CompetitorMonitoringRequest):
    logger.warning("[API] Direct competitor monitoring agent call detected. For full agentic workflow, use /agents/supervisor.")
    logger.info(f"[API] /agents/competitor-monitoring called with: {request}")
    try:
        result = run_competitor_monitoring_agent(request.product_data)
        logger.info(f"[API] Competitor monitoring agent result: {result}")
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Competitor monitoring completed successfully (note: for full agentic workflow, use /agents/supervisor)",
                "data": result.get("data")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"[API] Error in competitor monitoring agent: {e}")
        raise HTTPException(status_code=500, detail=f"Competitor monitoring failed: {str(e)}")

@app.post("/agents/supervisor")
async def run_supervisor(request: SupervisorRequest):
    logger.info(f"[API] /agents/supervisor called with: {request}")
    try:
        result = run_supervisor_agent({"products": request.products})
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
    """Get pricing history for a specific product"""
    try:
        from agents.supervisor_agent import supervisor_agent
        history = supervisor_agent.get_pricing_history(product_id, days)
        return {
            "status": "success",
            "product_id": product_id,
            "history": history
        }
    except Exception as e:
        logger.error(f"Error retrieving pricing history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pricing history: {str(e)}")

@app.get("/agents/competitor-monitoring/similar/{product_name}")
async def get_similar_products(product_name: str, category: str, limit: int = 5):
    """Get similar products using vector similarity search"""
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
        logger.error(f"Error finding similar products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar products: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)