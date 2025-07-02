from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from database_setup import ChatHistory

logger = logging.getLogger(__name__)

async def create_chat_record(db: Session, prompt: str, image_path: str):
    try:
        db_record = ChatHistory(
            prompt=prompt,
            image_path=image_path,
            created_at=datetime.utcnow()
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        logger.error(f"Error creating chat record: {e}")
        db.rollback()
        raise

async def get_chat_history(db: Session, skip: int = 0, limit: int = 10):
    try:
        return db.query(ChatHistory)\
                 .order_by(ChatHistory.created_at.desc())\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise

async def cleanup_old_records(db: Session, days: int = 30):
    try:
        threshold = datetime.utcnow() - timedelta(days=days)
        old_records = db.query(ChatHistory)\
                       .filter(ChatHistory.created_at < threshold)\
                       .all()
        
        for record in old_records:
            db.delete(record)
        
        db.commit()
        logger.info(f"Cleaned up {len(old_records)} old records")
    except Exception as e:
        logger.error(f"Error cleaning up old records: {e}")
        db.rollback()
        raise