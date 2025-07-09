from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models import *
from models.base import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Convert the PostgresDsn to string explicitly
database_url = str(settings.SQLALCHEMY_DATABASE_URI)
logger.debug(f"[DEBUG] SQLAlchemy database_url: {database_url}")

engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 10,
    },
    isolation_level='read committed'
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_competitor_prices(db, products):
    try:
        for product in products:
            db.add(CompetitorPrice(
                product_id=product["product_id"],
                product_name=product.get("product_name", None),
                category=product.get("category", None),
                competitor_name=product["competitor_name"],
                competitor_price=product["competitor_price"],
                scraped_at=product["scraped_at"],
                competitor_url=product.get("competitor_url", None),
                availability=product.get("availability", True),
                shipping_cost=product.get("shipping_cost", None),
                rating=product.get("rating", None),
                review_count=product.get("review_count", None),
                confidence_score=product.get("confidence_score", 1.0)
            ))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving competitor prices: {e}")
        raise

def save_agent_decision(db, decision_dict):
    try:
        decision = AgentDecision(**decision_dict)
        db.add(decision)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving agent decision: {e}")
        raise

def save_price_history(db, price_history_dict):
    try:
        price_history = PriceHistory(**price_history_dict)
        db.add(price_history)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving price history: {e}")
        raise

def save_product(db, product_dict):
    try:
        product = Product(**product_dict)
        db.add(product)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving product: {e}")
        raise

def save_demand_score(db, demand_score_dict):
    try:
        demand_score = DemandScore(**demand_score_dict)
        db.add(demand_score)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving demand score: {e}")
        raise

def save_inventory_level(db, inventory_level_dict):
    try:
        inventory_level = InventoryLevel(**inventory_level_dict)
        db.add(inventory_level)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving inventory level: {e}")
        raise

def save_feedback_log(db, feedback_log_dict):
    try:
        feedback_log = FeedbackLog(**feedback_log_dict)
        db.add(feedback_log)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving feedback log: {e}")
        raise

def save_sales_data(db, sales_data_dict):
    try:
        sales_data = SalesData(**sales_data_dict)
        db.add(sales_data)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving sales data: {e}")
        raise