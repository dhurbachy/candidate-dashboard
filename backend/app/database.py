from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./candidates.db")

engine=create_engine(
    DATABASE_URL,
    pool_pre_ping=True ,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=create_engine)