from sqlalchemy import Column, String, Numeric, Integer, DateTime
from src.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    id = Column(String(20), primary_key=True, index=True)
    name = Column(String(200))
    category = Column(String(100))
    base_price = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    cost_price = Column(Numeric(10, 2))
    stock_level = Column(Integer)
    demand_score = Column(Numeric(3, 2))
    last_updated = Column(DateTime)