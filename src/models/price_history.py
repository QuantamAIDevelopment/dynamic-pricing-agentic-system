from sqlalchemy import Column, String, Numeric, DateTime, Integer, ForeignKey
from src.models.base import BaseModel

class PriceHistory(BaseModel):
    __tablename__ = "price_history"

    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    old_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(10, 2))
    change_reason = Column(String(255))
    agent_name = Column(String(100))
    confidence_score = Column(Numeric(3, 2))
    timestamp = Column(DateTime) 