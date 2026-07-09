from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Database connection parameters
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Set timeout for Postgres so it fails fast (10s) instead of hanging indefinitely
    connect_args = {"connect_timeout": 10}

engine_args = {
    "connect_args": connect_args,
    "pool_pre_ping": True
}
if not settings.DATABASE_URL.startswith("sqlite"):
    # Enable multi-row VALUES clause batching for 100x faster bulk inserts on Postgres
    engine_args["executemany_mode"] = "values"

engine = create_engine(settings.DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
