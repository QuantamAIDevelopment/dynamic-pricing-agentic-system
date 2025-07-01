from config.database import get_db
from core.database import init_db
from sqlalchemy.exc import SQLAlchemyError

def check_db_connection():
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        return True
    except SQLAlchemyError:
        return False

def recreate_tables():
    from ..config.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    init_db()