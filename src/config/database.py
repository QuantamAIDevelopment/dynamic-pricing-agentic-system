from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from .settings import settings
from src.models.products import Product
from src.models.sales_data import SalesData
from src.models.competitor_prices import CompetitorPrice
from src.models.base import BaseModel  
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Database setup
database_url = settings.sqlalchemy_database_uri
engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10},
    isolation_level="READ COMMITTED"
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
BaseModel.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Get competitor prices and competitor names and current price
def get_competitor_prices(db, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.current_price is None:
        return 0.0
        

    avg_comp_price = db.query(func.avg(CompetitorPrice.competitor_price)).filter(
        CompetitorPrice.product_id == product_id
    ).scalar() or 0.0

    if avg_comp_price is None:
        return 0.0
    return (avg_comp_price - product.current_price) / product.current_price

 
# 2. Get sales in the last 30 days
def get_sales_last_30_days(db, product_id: str):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_quantity = db.query(func.sum(SalesData.quantity_sold)).filter(
        SalesData.product_id == product_id,
        SalesData.sale_date >= thirty_days_ago.date()
    ).scalar() or 0
    return total_quantity/30  # Average daily sales over the last 30 days

# 3. Get stock level
def get_stock_level(db, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    return product.stock_level if product else None