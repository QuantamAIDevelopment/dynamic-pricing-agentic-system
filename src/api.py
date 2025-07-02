from fastapi import FastAPI, HTTPException
from agents.web_scraping_agent import run_web_scraping_agent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Scraping API")

@app.get("/scrape")
async def scrape_domain(domain: str, category: str = "electronics", product_name: str = None):

    try:
        logger.info(f"Received API request for domain: {domain}, category: {category}, product_name: {product_name}")
        input_data = {"domain": domain, "category": category}
        if product_name:
            input_data["product_name"] = product_name
        result = run_web_scraping_agent(input_data)
        
        if result["status"] == "error":
            logger.error(f"Scraping failed: {result['message']}")
            raise HTTPException(status_code=500, detail=result["message"])
        
        logger.info(f"Scraping successful for {domain}, category: {category}, product_name: {product_name}")
        return result

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error in API: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)