from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from tools.search_tool import search_product_listing_page
from tools.scrape_tool import scrape_products, ScrapeProductInput
from config.database import get_db, CompetitorPrice

import logging
from datetime import datetime
from config.llm_config import llm
from models.products import Product  # Import here to avoid circular import
import urllib.parse
import redis
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tools = [
    Tool(
        name="search_product_listing_page",
        func=search_product_listing_page,
        description="Search for a product listing page on a competitor's website"
    ),
    Tool(
        name="scrape_products",
        func=scrape_products,
        description="Scrape a product listing page for pricing information"
    )
]

agent = initialize_agent(
    tools = tools,
    llm = llm,
    agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors = True,
    verbose = True
)

# Initialize Redis client for Pub/Sub
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def run_web_scraping_agent(input: dict) -> dict:

    domain = input.get("domain", "").strip()
    category = input.get("category", "").strip()
    product_name = input.get("product_name", None)

    logger.info(f"[WebScrapingAgent] Input received: domain={domain}, category={category}, product_name={product_name}")

    if not domain:
        logger.error("[WebScrapingAgent] Domain is required")
        return {
            "status": "error",
            "data": None,
            "message": "Error: Domain is required"
        }
    try:
        logger.info(f"[WebScrapingAgent] Running web scraping agent for {domain} in {category}")

        # Search for the best product listing URL
        search_input = {"domain": domain, "category": category}
        logger.info(f"[WebScrapingAgent] Invoking search_product_listing_page tool with input: {search_input}")
        search_result = search_product_listing_page.invoke({"input": search_input})
        logger.info(f"[WebScrapingAgent] search_product_listing_page result: {search_result}")
        best_url = None
        if isinstance(search_result, list) and search_result:
            if isinstance(search_result[0], dict):
                best_url = search_result[0].get("url")
            elif isinstance(search_result[0], str):
                best_url = search_result[0]
        elif isinstance(search_result, dict):
            best_url = search_result.get("url")
        elif isinstance(search_result, str):
            best_url = search_result
        logger.info(f"[WebScrapingAgent] Best product listing URL determined: {best_url}")
        # Clean up best_url if it has extra quotes
        if isinstance(best_url, str):
            best_url = best_url.strip().strip("'\"")
            if 'duckduckgo.com/l/?uddg=' in best_url:
                parsed = urllib.parse.urlparse(best_url)
                query = urllib.parse.parse_qs(parsed.query)
                uddg_url = query.get('uddg', [None])[0]
                if uddg_url:
                    best_url = urllib.parse.unquote(uddg_url)
        if not best_url:
            logger.error(f"[WebScrapingAgent] No product listing URL found for {domain} in {category}")
            return {
                "status": "error",
                "data": None,
                "message": "Error: No product listing URL found"
            }
        logger.info(f"[WebScrapingAgent] Best product listing URL found: {best_url}")
        # Scrape the product listing page
        scrape_input = {
            "url": best_url,
            "competitor": domain,
            "category": category,
            "product_name": product_name
        }
        logger.info(f"[WebScrapingAgent] Invoking scrape_products_core with input: {scrape_input}")
        from tools.scrape_tool import scrape_products_core
        scraped_products = scrape_products_core(
            scrape_input["url"],
            scrape_input["competitor"],
            scrape_input["category"],
            scrape_input["product_name"]
        )
        logger.info(f"[WebScrapingAgent] scrape_products_core returned {len(scraped_products) if scraped_products else 0} products")
        if not scraped_products:
            logger.error(f"[WebScrapingAgent] No products scraped for {domain} in {category}")
            return {
                "status": "error",
                "data": None,
                "message": "Error: No products scraped"
            }
        logger.info(f"[WebScrapingAgent] Scraped {len(scraped_products)} products for {domain} in {category}")
        # Return only the first (best) product
        best_product = scraped_products[0]
        logger.info(f"[WebScrapingAgent] Best product selected: {best_product}")
        # Publish to Redis for Competitor Monitoring Agent
        try:
            if 'scraped_at' not in best_product:
                best_product['scraped_at'] = datetime.now()
            logger.info(f"[WebScrapingAgent] Publishing scraped data to Redis: {best_product}")
            redis_client.publish('scraped_data', json.dumps(best_product, default=str))
            logger.info(f"[WebScrapingAgent] Published scraped data to Redis for product: {best_product.get('product_name', 'Unknown')}")
            redis_client.lpush('pending_competitor_data', json.dumps(best_product, default=str))
            logger.info(f"[WebScrapingAgent] Backed up scraped data to Redis list for product: {best_product.get('product_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"[WebScrapingAgent] Error publishing to Redis: {e}")
        return {
            "status": "success",
            "data": best_product,
            "message": "Successfully scraped and processed 1 product"
        }
    except Exception as e:
        logger.error(f"[WebScrapingAgent] Error in web scraping workflow: {e}")
        return {"status": "error", "data": None, "message": f"Error in workflow: {e}"}

if __name__ == "__main__":
    # Example usage with dynamic category
    input_data = {"domain": "amazon.com", "category": "books"}
    result = run_web_scraping_agent(input_data)
    print(result)
