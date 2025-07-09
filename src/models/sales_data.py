from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey, Text
from src.models.base import BaseModel

class SalesData(BaseModel):
    __tablename__ = "sales_data"
    
    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    quantity_sold = Column(Integer)
    sale_price = Column(Numeric(10, 2))
    sale_date = Column(DateTime)
    demand_signal = Column(Numeric(3, 2))  # Demand signal strength
    customer_segment = Column(String(50), nullable=True)  # Customer segment if available
    sales_channel = Column(String(50), nullable=True)  # Online, offline, etc.
    discount_applied = Column(Numeric(5, 2), nullable=True)  # Discount percentage if any
    transaction_id = Column(String(100), nullable=True)  # Unique transaction identifier 