from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey, Text, Boolean
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
    sales_velocity = Column(Numeric(10, 2))  # Units sold per day
    price_elasticity = Column(Numeric(5, 2))  # Price sensitivity
    market_position = Column(String(50))  # premium, mid-range, budget
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime)

class DemandScore(BaseModel):
    __tablename__ = "demand_scores"
    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    demand_score = Column(Numeric(3, 2))
    sales_velocity = Column(Numeric(10, 2))
    price_advantage_pct = Column(Numeric(10, 2))
    stock_level = Column(Integer)
    llm_explanation = Column(Text)  # Changed from String(255) to Text for longer explanations
    calculated_at = Column(DateTime)

class InventoryLevel(BaseModel):
    __tablename__ = "inventory_levels"
    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    stock_level = Column(Integer)
    reorder_point = Column(Integer)  # Minimum stock level before reordering
    max_stock = Column(Integer)  # Maximum stock level
    last_updated = Column(DateTime)