from sqlalchemy import Column,Integer,Numeric, ForeignKey, String, DateTime
from models.base import BaseModel

class CompetitorPrice(BaseModel):
    __tablename__ = "competitor_prices"

    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    competitor_name = Column(String(100))
    competitor_price = Column(Numeric(10,2))
    scraped_at = Column(DateTime)
