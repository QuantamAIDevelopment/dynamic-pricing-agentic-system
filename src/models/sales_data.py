from sqlalchemy import Column, Integer, String, Float, DateTime
from src.models.base import BaseModel

class SalesData(BaseModel):
    __tablename__ = "sales_data"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(20), index=True)
    quantity_sold = Column(Integer)
    sale_price = Column(Float)
    sale_date = Column(DateTime)
    total_revenue = Column(Float)
    demand_signal = Column(Float)