from ..config.database import get_db
from src.core.database import init_db
from sqlalchemy.exc import SQLAlchemyError

def check_database_connection():
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        return False

def recreate_tables():
    from ..config.database import BaseModel, engine
    from src.core.database import init_db
    init_db()