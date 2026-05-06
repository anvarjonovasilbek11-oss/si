"""
Database initialization script
Run this to create all tables and optionally seed sample data
"""
from database import Base, engine, SessionLocal
from models import Employee, HRDoc, UserQuery
from datetime import date, datetime


def init_database():
    """Initialize database tables"""
    print("🔧 Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!\n")
        
        # Print table information
        print("📊 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  ✓ {table_name}")
        
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def seed_sample_data():
    """Add sample data to the database"""
    print("\n🌱 Seeding sample data...")
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Employee).first():
            print("⚠ Sample data already exists. Skipping seed.")
            return
        
        # Sample employees
        employees = [
            Employee(
                full_name="John Doe",
                department="Engineering",
                position="Senior Software Engineer",
                hire_date=date(2020, 1, 15),
                email="john.doe@company.com"
            ),
            Employee(
                full_name="Jane Smith",
                department="Human Resources",
                position="HR Manager",
                hire_date=date(2019, 3, 10),
                email="jane.smith@company.com"
            ),
            Employee(
                full_name="Mike Johnson",
                department="Marketing",
                position="Marketing Specialist",
                hire_date=date(2021, 6, 1),
                email="mike.johnson@company.com"
            )
        ]
        
        # Sample HR documents
        hr_docs = [
            HRDoc(
                title="Employee Handbook 2024",
                content="This is the official employee handbook containing company policies, procedures, and guidelines for all employees."
            ),
            HRDoc(
                title="Leave Policy",
                content="Employees are entitled to 15 days of paid leave per year. Leave requests must be submitted at least 2 weeks in advance."
            ),
            HRDoc(
                title="Code of Conduct",
                content="All employees must maintain professional behavior, respect colleagues, and adhere to company values and ethics."
            )
        ]
        
        # Sample user queries
        user_queries = [
            UserQuery(
                user_id=1,
                query_text="What is the leave policy?",
                answer_text="Employees are entitled to 15 days of paid leave per year.",
                timestamp=datetime.now()
            )
        ]
        
        # Add all sample data
        db.add_all(employees)
        db.add_all(hr_docs)
        db.add_all(user_queries)
        db.commit()
        
        print(f"✓ Added {len(employees)} employees")
        print(f"✓ Added {len(hr_docs)} HR documents")
        print(f"✓ Added {len(user_queries)} user queries")
        print("\n✅ Sample data seeded successfully!")
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


def verify_database():
    """Verify database setup by querying tables"""
    print("\n🔍 Verifying database setup...")
    db = SessionLocal()
    
    try:
        employee_count = db.query(Employee).count()
        doc_count = db.query(HRDoc).count()
        query_count = db.query(UserQuery).count()
        
        print(f"  📋 Employees: {employee_count}")
        print(f"  📄 HR Documents: {doc_count}")
        print(f"  💬 User Queries: {query_count}")
        print("\n✅ Database verification complete!")
        
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("HR Bot Database Initialization")
    print("=" * 60)
    
    # Initialize database
    if init_database():
        # Seed sample data
        seed_sample_data()
        
        # Verify setup
        verify_database()
    
    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)
