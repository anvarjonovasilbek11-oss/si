"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    echo=Config.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes
    Provides database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    from models import ChatLog, User
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
