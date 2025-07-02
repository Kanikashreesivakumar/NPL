from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

DATABASE_URL = "sqlite:///./chat_history.db"
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    async def cleanup_old_records(cls, session):
        threshold = datetime.utcnow() - timedelta(days=30)
        old_records = session.query(cls).filter(cls.created_at < threshold).all()
        
        for record in old_records:
            if os.path.exists(record.image_path):
                os.remove(record.image_path)
            session.delete(record)
        
        session.commit()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)