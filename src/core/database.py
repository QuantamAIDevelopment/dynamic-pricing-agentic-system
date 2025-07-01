from sqlalchemy.exc import SQLAlchemyError
from config.database import SessionLocal, engine, Base
# Ensure all models are imported so their tables are created
from models import products, competitor_prices, agent_decisions
import time
import logging

logger = logging.getLogger(__name__)

def init_db(max_retries: int = 5, delay: int = 2):
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to database (attempt {retry_count + 1})")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return
        except SQLAlchemyError as e:
            retry_count += 1
            logger.error(f"Database connection failed (attempt {retry_count}): {str(e)}")
            if retry_count == max_retries:
                logger.error("Max retries reached. Could not connect to database.")
                raise
            time.sleep(delay)