import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

try:
    engine = create_engine(DATABASE_URL, echo=False)
    print("Database connection established.")
except Exception as e:
    print("Database connection failed:", e)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
