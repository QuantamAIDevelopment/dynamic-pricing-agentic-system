from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Convert the PostgresDsn to string explicitly
database_url = str(settings.SQLALCHEMY_DATABASE_URI)
print(f"[DEBUG] SQLAlchemy database_url: {database_url}")

engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 10,
        # "options": "-c default_transaction_isolation=read committed"
    },
    isolation_level='read committed'
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()