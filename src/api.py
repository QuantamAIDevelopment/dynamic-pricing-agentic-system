from fastapi import FastAPI, HTTPException
from src.config.database import get_db
from src.agents.demand_analysis_agent import analyze_demand_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/demand_score")
async def get_demand_score(product_id: str):
    db = next(get_db())
    
    try:
        result = analyze_demand_score(db, product_id)
        return result
    except Exception as e:
        logger.error(f"Error fetching demand score for product {product_id}: str{e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)