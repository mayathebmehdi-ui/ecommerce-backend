from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)
    shipping_policy = Column(Text, nullable=True)
    shipping_url = Column(String(500), nullable=True)
    return_policy = Column(Text, nullable=True)
    return_url = Column(String(500), nullable=True)
    self_help_returns = Column(String(500), nullable=True)
    self_help_url = Column(String(500), nullable=True)
    insurance = Column(String(500), nullable=True)
    insurance_url = Column(String(500), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    url = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
