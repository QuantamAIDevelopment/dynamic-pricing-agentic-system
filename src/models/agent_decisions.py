from sqlalchemy import Column, String, DateTime, Text, Numeric, ForeignKey
from models.base import BaseModel

class AgentDecision(BaseModel):
    __tablename__ = "agent_decisions"
    
    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    agent_name = Column(String(100))
    decision_type = Column(String(100))
    input_data = Column(Text)
    output_data = Column(Text)
    confidence_score = Column(Numeric(3, 2))
    explanation = Column(Text)
    timestamp = Column(DateTime)