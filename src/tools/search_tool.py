from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from config.database import get_db, CompetitorPrice
from models.products import Product
import logging
import re
from datetime import datetime
import time
import json
from typing import Union
import hashlib
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_product_id_from_url(url: str) -> str:
    """Generate a unique product ID from URL using SHA1 hash."""
    return hashlib.sha1(url.encode()).hexdigest()[:20]

def clean_domain(domain: str) -> str:
    """Cleans and normalizes domain names."""
    domain = domain.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
    parsed = urlparse(f"https://{domain}")
    return parsed.netloc or parsed.path

def is_valid_amazon_url(url):
    # Accept only main www.amazon.com product or search/category URLs
    return bool(re.match(r"^https://www\.amazon\.com/(s|dp/)", url))

@tool("search_product_listing_page")
def search_product_listing_page(input: Union[dict, str]) -> list[dict]:
    """
    Searches for product listing pages on competitor websites and stores results.

    Args:
        input (dict or str): {
            "domain": "example.com",
            "category": "electronics"
        } or a comma-separated string like "example.com,electronics"

    Returns:
        list[dict]: List of dictionaries containing search results or homepage fallback
    """

    domain = None
    query = None
    if isinstance(input, dict):
        # Always use product_name as the query if provided
        query = input.get("product_name") or input.get("category")
        domain = input.get("domain", "amazon").lower()
    elif isinstance(input, str):
        domain = "amazon"
        query = input
    logger.info(f"Search tool input: domain={domain}, query={query}")
    if not query:
        logger.error("No product_name or category provided to search tool.")
        return []
    from urllib.parse import quote_plus
    if domain in ["flipkart", "flipkart.com"]:
        url = f"https://www.flipkart.com/search?q={quote_plus(query)}"
        logger.info(f"Constructed Flipkart search URL: {url}")
        return [url]
    elif domain in ["amazon", "amazon.com", "amazon.in"]:
        url = f"https://www.amazon.in/s?k={quote_plus(query)}"
        logger.info(f"Constructed Amazon search URL: {url}")
        return [url]
    logger.error(f"Unsupported domain: {domain}")
    return []
