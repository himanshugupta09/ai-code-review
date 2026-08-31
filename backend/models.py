import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class ReviewSession(Base):
    __tablename__ = "review_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    repo_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    findings = relationship(
        "Finding", back_populates="session", cascade="all, delete-orphan"
    )


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("review_sessions.id"), nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    severity = Column(String, nullable=False)  
    message = Column(Text, nullable=False)
    source = Column(String, nullable=False)

    session = relationship("ReviewSession", back_populates="findings")