from langchain.tools import tool
from pydantic import BaseModel, Field
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from src.config.database import get_db, save_competitor_prices
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import difflib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Input schema
class ScrapeProductInput(BaseModel):
    url: str = Field(..., description="The product listing page URL to scrape")
    competitor: str = Field(..., description="The competitor name (e.g., 'Amazon')")
    category: str = Field(..., description="The product category (e.g., 'books')")
    product_name: str = Field(None, description="Optional: precise product name to filter results")

# Simple keyword-based category inference
CATEGORY_KEYWORDS = {
    'laptop': 'Electronics',
    'phone': 'Electronics',
    'mobile': 'Electronics',
    'book': 'Books',
    'bike': 'Automotive',
    'car': 'Automotive',
    'shoe': 'Footwear',
    'shirt': 'Apparel',
    't-shirt': 'Apparel',
    'refrigerator': 'Appliances',
    'tv': 'Electronics',
    'television': 'Electronics',
    'headphone': 'Electronics',
    'camera': 'Electronics',
    'watch': 'Accessories',
    'bag': 'Accessories',
    'tablet': 'Electronics',
    'microwave': 'Appliances',
    'washing machine': 'Appliances',
    'ac ': 'Appliances',
    'air conditioner': 'Appliances',
    'sofa': 'Furniture',
    'bed': 'Furniture',
    'fan': 'Appliances',
    'printer': 'Electronics',
    'monitor': 'Electronics',
    'mouse': 'Electronics',
    'keyboard': 'Electronics',
    'dress': 'Apparel',
    'jeans': 'Apparel',
    'tablet': 'Electronics',
    'earbud': 'Electronics',
    'speaker': 'Electronics',
    'bottle': 'Home & Kitchen',
    'mixer': 'Appliances',
    'grinder': 'Appliances',
    'oven': 'Appliances',
    'cooktop': 'Appliances',
    'guitar': 'Musical Instruments',
    'piano': 'Musical Instruments',
    'drum': 'Musical Instruments',
    'cycle': 'Sports',
    'bat': 'Sports',
    'ball': 'Sports',
    'helmet': 'Automotive',
    'tyre': 'Automotive',
    'oil': 'Automotive',
    'tablet': 'Electronics',
    'air fryer': 'Appliances',
    'trimmer': 'Personal Care',
    'shaver': 'Personal Care',
    'perfume': 'Personal Care',
    'cream': 'Personal Care',
    'lotion': 'Personal Care',
    'soap': 'Personal Care',
    'toothpaste': 'Personal Care',
    'toothbrush': 'Personal Care',
    'bag': 'Accessories',
    'wallet': 'Accessories',
    'belt': 'Accessories',
    'sandal': 'Footwear',
    'slipper': 'Footwear',
    'boot': 'Footwear',
    'jacket': 'Apparel',
    'sweater': 'Apparel',
    'blender': 'Appliances',
    'juicer': 'Appliances',
    'camera': 'Electronics',
    'tripod': 'Electronics',
    'lens': 'Electronics',
    'router': 'Electronics',
    'modem': 'Electronics',
    'projector': 'Electronics',
    'tablet': 'Electronics',
    'pen': 'Stationery',
    'notebook': 'Stationery',
    'diary': 'Stationery',
    'lamp': 'Home & Kitchen',
    'cooker': 'Appliances',
    'pan': 'Home & Kitchen',
    'mug': 'Home & Kitchen',
    'plate': 'Home & Kitchen',
    'bowl': 'Home & Kitchen',
    'fork': 'Home & Kitchen',
    'spoon': 'Home & Kitchen',
    'knife': 'Home & Kitchen',
    'towel': 'Home & Kitchen',
    'blanket': 'Home & Kitchen',
    'pillow': 'Home & Kitchen',
    'mattress': 'Home & Kitchen',
    'curtain': 'Home & Kitchen',
    'carpet': 'Home & Kitchen',
    'rug': 'Home & Kitchen',
    'broom': 'Home & Kitchen',
    'mop': 'Home & Kitchen',
    'bucket': 'Home & Kitchen',
    'brush': 'Home & Kitchen',
    'detergent': 'Home & Kitchen',
    'cleaner': 'Home & Kitchen',
    'soap': 'Personal Care',
    'shampoo': 'Personal Care',
    'conditioner': 'Personal Care',
    'toothpaste': 'Personal Care',
    'toothbrush': 'Personal Care',
    'razor': 'Personal Care',
    'blade': 'Personal Care',
    'comb': 'Personal Care',
    'mirror': 'Personal Care',
    'scissors': 'Personal Care',
    'clipper': 'Personal Care',
    'nail': 'Personal Care',
    'file': 'Personal Care',
    'tweezer': 'Personal Care',
    'cotton': 'Personal Care',
    'swab': 'Personal Care',
    'bandage': 'Personal Care',
    'ointment': 'Personal Care',
    'tablet': 'Electronics',
    'capsule': 'Personal Care',
    'syrup': 'Personal Care',
    'drop': 'Personal Care',
    'spray': 'Personal Care',
    'inhaler': 'Personal Care',
    'mask': 'Personal Care',
    'sanitizer': 'Personal Care',
    'glove': 'Personal Care',
    'thermometer': 'Personal Care',
    'stethoscope': 'Personal Care',
    'bp': 'Personal Care',
    'monitor': 'Electronics',
    'pulse': 'Personal Care',
    'oximeter': 'Personal Care',
    'wheelchair': 'Personal Care',
    'walker': 'Personal Care',
    'crutch': 'Personal Care',
    'stick': 'Personal Care',
    'hearing': 'Personal Care',
    'aid': 'Personal Care',
    'spectacle': 'Personal Care',
    'glass': 'Personal Care',
    'contact': 'Personal Care',
    'lens': 'Personal Care',
    'frame': 'Personal Care',
    'case': 'Personal Care',
    'solution': 'Personal Care',
    'spray': 'Personal Care',
    'drop': 'Personal Care',
    'ointment': 'Personal Care',
    'cream': 'Personal Care',
    'gel': 'Personal Care',
    'powder': 'Personal Care',
}

def infer_category_from_name(product_name: str) -> str:
    if not product_name:
        return "Unknown"
    name_lower = product_name.lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in name_lower:
            logger.info(f"[Category Inference] Inferred category '{category}' from product name '{product_name}' using keyword '{keyword}'")
            return category
    return "Unknown"

# Move scraping logic to a helper function

def scrape_products_core(url: str, competitor: str, category: str, product_name: str = None) -> list[dict]:
    options = Options()
    # For debugging, you can comment out headless mode
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    # Add more browser-like headers if needed
    options.add_argument("--window-size=1920,1080")
    # You can add more headers via CDP if needed
    driver = webdriver.Chrome(options=options)
    products = []
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JS to load
        if 'flipkart.com' in url:
            # Step 1: Open Flipkart homepage
            driver.get('https://www.flipkart.com')
            time.sleep(2)
            # Step 1.5: Close login popup if present
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, 'button._2KpZ6l._2doB4z')
                close_btn.click()
                time.sleep(1)
            except Exception:
                pass
            # Step 2: Enter category in the search bar and submit
            try:
                wait = WebDriverWait(driver, 10)
                try:
                    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="q"]')))
                except Exception:
                    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[title="Search for products, brands and more"]')))
                search_box.clear()
                search_box.send_keys(category)
                search_box.submit()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error entering category in Flipkart search bar: {e}")
                driver.save_screenshot('flipkart_searchbar_error.png')
            # Step 3: Enter product name in the search bar and submit
            try:
                wait = WebDriverWait(driver, 10)
                try:
                    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="q"]')))
                except Exception:
                    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[title="Search for products, brands and more"]')))
                search_box.clear()
                search_box.send_keys(product_name)
                search_box.submit()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error entering product name in Flipkart search bar: {e}")
                driver.save_screenshot('flipkart_searchbar_error.png')
            # Step 4: Scrape the resulting product listing page (Amazon-style)
            try:
                wait = WebDriverWait(driver, 10)
                # Try multiple selectors for product cards
                card_selectors = [
                    'div._75nlfW',  # New: main product card
                    'div._1AtVbE', 'div._2kHMtA', 'div._4ddWXP', 'div._2rpwqI'
                ]
                product_cards = []
                for selector in card_selectors:
                    cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        product_cards = cards
                        break
                logger.info(f"Found {len(product_cards)} Flipkart product cards on listing page.")
                scraped_names = []
                products = []
                for card in product_cards:
                    try:
                        # Try multiple selectors for product link
                        link_elem = None
                        link_selectors = [
                            'a.CGtC98',  # New: main product link
                            'a._1fQZEK', 'a.s1Q9rs', 'a.IRpwTa', 'a._2rpwqI'
                        ]
                        for selector in link_selectors:
                            links = card.find_elements(By.CSS_SELECTOR, selector)
                            if links:
                                link_elem = links[0]
                                break
                        if not link_elem:
                            continue
                        product_url = link_elem.get_attribute('href')
                        # Try multiple selectors for product name
                        name = ''
                        name_selectors = [
                            'div.KzDlHZ',  # New: main product name
                            'div._4rR01T', 'a.s1Q9rs', 'div._2WkVRV', 'div._3wU53n'
                        ]
                        for sel in name_selectors:
                            try:
                                name = card.find_element(By.CSS_SELECTOR, sel).text.strip()
                                if name:
                                    break
                            except Exception:
                                continue
                        # Try multiple selectors for price
                        detail_price = None
                        price_selectors = [
                            'div.Nx9bqj._4b5DiR',  # Main product price (from provided HTML)
                            'div._4b5DiR',         # Fallback: price class without Nx9bqj
                            'div.cN1yYO .Nx9bqj',  # Fallback: price inside cN1yYO
                            'div._30jeq3', 'div._1vC4OE', 'div._25b18c ._30jeq3', 'div._30jeq3._16Jk6d',
                            'div._16Jk6d', 'div._3I9_wc', 'div._2p6lqe', 'div._2Tpdn3',
                            'div._1_WHN1', 'div._2r_T1I', 'div._1AtVbE ._30jeq3',
                            'div._1vC4OE._2r_T1I', 'div._30jeq3._1_WHN1',
                        ]
                        for sel in price_selectors:
                            try:
                                price_text = card.find_element(By.CSS_SELECTOR, sel).text
                                logger.info(f"[Flipkart Scraper] Found price text '{price_text}' using selector '{sel}'")
                                detail_price = float(price_text.replace('₹', '').replace(',', '').strip())
                                break
                            except Exception:
                                continue
                        # If detail_price is still None, log the card HTML for debugging
                        if detail_price is None:
                            try:
                                card_html = card.get_attribute('outerHTML')
                                logger.error(f"[Flipkart Scraper] Could not find price for card. HTML: {card_html}")
                                with open('flipkart_price_debug.html', 'a', encoding='utf-8') as f:
                                    f.write(card_html + '\n\n')
                            except Exception as e:
                                logger.error(f"[Flipkart Scraper] Error logging card HTML: {e}")
                        # Try to extract category from breadcrumbs or page metadata
                        category_value = None
                        try:
                            # Flipkart: Breadcrumbs are often in '._2whKao' or '._1MR4o5' classes
                            breadcrumb_selectors = ['._2whKao', '._1MR4o5', 'nav.breadcrumbs', '.breadcrumb']
                            for sel in breadcrumb_selectors:
                                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                                if elems:
                                    category_value = ' > '.join([e.text for e in elems if e.text])
                                    break
                        except Exception:
                            category_value = None
                        if not category_value or category_value == "Unknown":
                            category_value = infer_category_from_name(name)
                        scraped_names.append(name)
                        if name and detail_price is not None:
                            product = {
                                "product_id": hashlib.sha1(product_url.encode()).hexdigest()[:20],
                                "product_name": name,
                                "category": category_value,
                                "competitor_name": competitor,
                                "competitor_price": detail_price,
                                "product_url": product_url,
                                "scraped_at": datetime.utcnow()
                            }
                            products.append(product)
                    except Exception as e:
                        continue
                logger.info(f"Scraped product names: {scraped_names}")
                # Substring match for product_name (case-insensitive)
                matched_product = None
                if product_name and products:
                    for p in products:
                        if product_name.strip().lower() in p["product_name"].strip().lower():
                            matched_product = p
                            logger.info(f"[Scraper] Matched product: '{p['product_name']}' for input '{product_name}'")
                            break
                if matched_product:
                    products = [matched_product]
                else:
                    products = []
                # Store found products in the database
                if products:
                    with next(get_db()) as db:
                        save_competitor_prices(db, products)
                return products[:1] if products else []
            except Exception as e:
                logger.error(f"Error scraping Flipkart product listing: {e}")
                with open('flipkart_scrape_exception_debug.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                return []
        elif 'amazon.in' in url or 'amazon.com' in url:
            # Step 1: Open Amazon.in homepage
            driver.get('https://www.amazon.in')
            time.sleep(2)
            # Step 2: Enter category in the search bar and submit
            try:
                search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
                search_box.clear()
                search_box.send_keys(category)
                search_box.submit()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error entering category in Amazon search bar: {e}")
            # Step 3: Enter product name in the search bar and submit
            try:
                search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
                search_box.clear()
                search_box.send_keys(product_name)
                search_box.submit()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error entering product name in Amazon search bar: {e}")
            # Step 4: Scrape the resulting product listing page
            product_cards = driver.find_elements(By.CSS_SELECTOR, '.s-result-item[data-asin]')
            logger.info(f"Found {len(product_cards)} Amazon product cards after two-step search.")
            scraped_names = []
            products = []
            for card in product_cards:
                try:
                    try:
                        name_tag = card.find_element(By.CSS_SELECTOR, 'span.a-size-medium.a-color-base.a-text-normal')
                    except Exception:
                        name_tag = card.find_element(By.CSS_SELECTOR, 'h2 span')
                    try:
                        price_whole = card.find_element(By.CSS_SELECTOR, '.a-price-whole')
                        price_frac = card.find_element(By.CSS_SELECTOR, '.a-price-fraction')
                        price = float(f"{price_whole.text.replace(',', '')}.{price_frac.text.strip()}")
                    except Exception:
                        price_tag = card.find_element(By.CSS_SELECTOR, 'span.a-price')
                        price = float(price_tag.text.replace('₹', '').replace(',', '').replace('$', '').strip())
                    name = name_tag.text.strip()
                    # Try to extract category from breadcrumbs or page metadata (Amazon)
                    category_value = None
                    try:
                        breadcrumb_selectors = ['nav.a-breadcrumb', '.a-unordered-list.a-horizontal.a-size-small', '.breadcrumb']
                        for sel in breadcrumb_selectors:
                            elems = card.find_elements(By.CSS_SELECTOR, sel)
                            if elems:
                                category_value = ' > '.join([e.text for e in elems if e.text])
                                break
                    except Exception:
                        category_value = None
                    if not category_value or category_value == "Unknown":
                        category_value = infer_category_from_name(name)
                    scraped_names.append(name)
                    asin = card.get_attribute('data-asin') or f"{competitor}-{name[:30]}"
                    product = {
                        "product_id": asin,
                        "product_name": name,
                        "category": category_value,
                        "competitor_name": competitor,
                        "competitor_price": price,
                        "scraped_at": datetime.utcnow()
                    }
                    products.append(product)
                except Exception as e:
                    continue
            logger.info(f"Scraped product names: {scraped_names}")
            # Substring match for product_name (case-insensitive) for Amazon
            matched_product = None
            if product_name and products:
                for p in products:
                    if product_name.strip().lower() in p["product_name"].strip().lower():
                        matched_product = p
                        logger.info(f"[Scraper] Matched product: '{p['product_name']}' for input '{product_name}'")
                        break
            if matched_product:
                products = [matched_product]
            else:
                products = []
            # Store found products in the database
            if products:
                with next(get_db()) as db:
                    save_competitor_prices(db, products)
            return products[:1] if products else []
        else:
            with open('unknown_platform_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.error("Unknown platform. Saved page source to unknown_platform_debug.html.")
            return []
    except Exception as e:
        logger.error(f"Error scraping {url} with Selenium: {e}")
        return []
    finally:
        driver.quit()

@tool("scrape_products", args_schema=ScrapeProductInput)
def scrape_products(input: ScrapeProductInput) -> list[dict]:
    """
    Scrapes products from a competitor page and saves them to the database.
    Args:
        input (ScrapeProductInput): {
            "url": "https://...",
            "competitor": "Amazon",
            "category": "books",
            "product_name": "Harry Potter"
        }
    Returns:
        list[dict]: List of product data dicts or empty list on error
    """
    return scrape_products_core(input.url, input.competitor, input.category, input.product_name)
