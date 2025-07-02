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

def run_web_scraping_agent(input: dict) -> dict:

    domain = input.get("domain", "").strip()
    category = input.get("category", "").strip()
    product_name = input.get("product_name", None)

    if not domain:
        logger.error("Domain is required")
        return {
            "status": "error",
            "data": None,
            "message": "Error: Domain is required"
        }
    try:
        logger.info(f"Running web scraping agent for {domain} in {category}")

        # Search for the best product listing URL
        search_input = {"domain": domain, "category": category}
        search_result = search_product_listing_page.invoke({"input": search_input})
        best_url = None
        if isinstance(search_result, list) and search_result:
            # Handle both list of dicts and list of strings
            if isinstance(search_result[0], dict):
                best_url = search_result[0].get("url")
            elif isinstance(search_result[0], str):
                best_url = search_result[0]
        elif isinstance(search_result, dict):
            best_url = search_result.get("url")
        elif isinstance(search_result, str):
            best_url = search_result
        
        # Clean up best_url if it has extra quotes
        if isinstance(best_url, str):
            best_url = best_url.strip().strip("'\"")
            # If the URL is a DuckDuckGo redirect, extract the real URL
            if 'duckduckgo.com/l/?uddg=' in best_url:
                parsed = urllib.parse.urlparse(best_url)
                query = urllib.parse.parse_qs(parsed.query)
                uddg_url = query.get('uddg', [None])[0]
                if uddg_url:
                    best_url = urllib.parse.unquote(uddg_url)

        if not best_url:
            logger.error(f"No product listing URL found for {domain} in {category}")
            return {
                "status": "error",
                "data": None,
                "message": "Error: No product listing URL found"
            }
        logger.info(f"Best product listing URL found: {best_url}")

        # Scrape the product listing page
        scrape_input = {
            "url": best_url,
            "competitor": domain,
            "category": category,
            "product_name": product_name
        }
        # Use the core function directly to avoid LangChain tool invocation issues
        from tools.scrape_tool import scrape_products_core
        scraped_products = scrape_products_core(
            scrape_input["url"],
            scrape_input["competitor"],
            scrape_input["category"],
            scrape_input["product_name"]
        )
        if not scraped_products:
            logger.error(f"No products scraped for {domain} in {category}")
            return {
                "status": "error",
                "data": None,
                "message": "Error: No products scraped"
            }
        logger.info(f"Scraped {len(scraped_products)} products for {domain} in {category}")

        # Return only the first (best) product
        best_product = scraped_products[0]
        return {
            "status": "success",
            "data": best_product,
            "message": "Successfully scraped and processed 1 product"
        }
    
    except Exception as e:
        logger.error(f"Error in web scraping workflow: {e}")
        return {"status": "error", "data": None, "message": f"Error in workflow: {e}"}

if __name__ == "__main__":
    # Example usage with dynamic category
    input_data = {"domain": "amazon.com", "category": "books"}
    result = run_web_scraping_agent(input_data)
    print(result)
