import dotenv
dotenv.load_dotenv()
from pydantic.v1 import validator
from pydantic_settings import BaseSettings
from typing import Optional
import urllib.parse


class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Dinesh@4"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "Pricing_db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()