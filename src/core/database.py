
from sqlalchemy.exc import SQLAlchemyError
from ..config.database import SessionLocal, engine, BaseModel
import logging
import time

logger = logging.getLogger(__name__)

def init_db(max_retries: int = 5, delay: int = 2):
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to the database (attempt {retry_count + 1})")
            BaseModel.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            break
        except SQLAlchemyError as e:
            retry_count += 1
            logger.error(f"Database connection failed (attempt {retry_count}): {str(e)}")
            if retry_count >= max_retries:
                logger.info("Max retries reached. Could not connect to the database.")
                raise
            time.sleep(delay)