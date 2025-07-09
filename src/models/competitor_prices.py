from sqlalchemy import Column, Integer, Numeric, ForeignKey, String, DateTime, Text, Boolean
from models.base import BaseModel

class CompetitorPrice(BaseModel):
    __tablename__ = "competitor_prices"

    product_id = Column(String(50), index=True)
    product_name = Column(String(255))
    category = Column(String(100))
    competitor_name = Column(String(100))
    competitor_price = Column(Numeric(10,2))
    competitor_url = Column(String(500))  # URL where price was scraped
    availability = Column(Boolean, default=True)  # Whether product is available
    shipping_cost = Column(Numeric(10,2), nullable=True)  # Shipping cost if available
    rating = Column(Numeric(3,2), nullable=True)  # Product rating
    review_count = Column(Integer, nullable=True)  # Number of reviews
    scraped_at = Column(DateTime)
    confidence_score = Column(Numeric(3,2), default=1.0)  # Confidence in scraped data
