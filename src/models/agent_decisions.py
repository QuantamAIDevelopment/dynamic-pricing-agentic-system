from sqlalchemy import Column, String, DateTime, Text, Numeric, ForeignKey, JSON
from src.models.base import BaseModel

class AgentDecision(BaseModel):
    __tablename__ = "agent_decisions"
    
    product_id = Column(String(20), ForeignKey("products.id"), index=True)
    agent_name = Column(String(100))
    decision_type = Column(String(100))
    input_data = Column(Text)
    output_data = Column(Text)
    confidence_score = Column(Numeric(3, 2))
    explanation = Column(Text)
    reflection = Column(Text)  # Agent's reflection on the decision
    reasoning_chain = Column(JSON)  # Step-by-step reasoning
    timestamp = Column(DateTime)

class FeedbackLog(BaseModel):
    __tablename__ = "feedback_log"
    
    agent_name = Column(String(100))
    feedback_type = Column(String(100))
    message = Column(Text)
    related_product_id = Column(String(20), ForeignKey("products.id"), index=True, nullable=True)
    severity = Column(String(20))  # info, warning, error, critical
    action_taken = Column(Text)  # What action was taken based on feedback
    timestamp = Column(DateTime)