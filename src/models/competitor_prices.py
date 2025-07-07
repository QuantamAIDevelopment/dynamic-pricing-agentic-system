from sqlalchemy import Column,Integer,Numeric, ForeignKey, String, DateTime
from src.models.base import BaseModel

class CompetitorPrice(BaseModel):
    __tablename__ = "competitor_prices"

    product_id = Column(String(50), index=True)
    product_name = Column(String(255))
    category = Column(String(100))
    competitor_name = Column(String(100))
    competitor_price = Column(Numeric(10,2))
    scraped_at = Column(DateTime)