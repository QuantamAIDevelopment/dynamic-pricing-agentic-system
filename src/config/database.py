from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models.competitor_prices import CompetitorPrice
from models.base import Base
from models.products import Product
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
                scraped_at=product["scraped_at"]
            ))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving competitor prices: {e}")
        raise