"""
SQLAlchemy models for HR Bot database
Supports multilingual HR documents and feedback
"""
from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, Float, func
from database import Base, engine
from datetime import datetime

# Check if pgvector extension is available in the database
# For now, we'll use Text type as pgvector extension is not installed
# To enable vector support:
# 1. Install: sudo apt-get install postgresql-16-pgvector
# 2. Enable in database: CREATE EXTENSION vector;
# 3. Set VECTOR_AVAILABLE = True below
VECTOR_AVAILABLE = False  # Set to True after installing pgvector

# Try to import pgvector support (but don't use it unless extension is enabled)
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None  # Fallback


class Employee(Base):
    """
    Employee model to store employee information
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.full_name}', department='{self.department}')>"


class HRDoc(Base):
    """
    HR Document model to store HR policies, handbooks, and other documents
    with vector embeddings for semantic search
    """
    __tablename__ = "hr_docs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # Using VECTOR type for pgvector support (dimension 768 for common embeddings)
    # Falls back to Text if pgvector is not enabled
    embedding = Column(Vector(768) if VECTOR_AVAILABLE else Text, nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HRDoc(id={self.id}, title='{self.title[:50]}...')>"


class UserQuery(Base):
    """
    User Query model to store user questions and AI-generated answers
    for analytics and improvement
    """
    __tablename__ = "user_queries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<UserQuery(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"


class HRDocument(Base):
    """
    Multilingual HR Document model with vector embeddings
    Supports Uzbek, Russian, and English documents
    """
    __tablename__ = "hr_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    language = Column(String(5), nullable=False, index=True)  # 'uz', 'ru', 'en'
    # Vector embedding for semantic search (768 dimensions)
    embedding = Column(Vector(768) if VECTOR_AVAILABLE else Text, nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HRDocument(id={self.id}, title='{self.title[:50]}', lang='{self.language}')>"


class HRFeedback(Base):
    """
    User feedback model for tracking question-answer quality
    Supports multilingual feedback collection
    """
    __tablename__ = "hr_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    language = Column(String(5), nullable=False, index=True)  # 'uz', 'ru', 'en'
    rating = Column(Float, nullable=True)  # User rating (e.g., 1-5 stars)
    
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<HRFeedback(id={self.id}, lang='{self.language}', rating={self.rating})>"


# Create all tables in the database
if __name__ == "__main__":
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")
        
        # Print table information
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
