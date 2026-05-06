"""
Create new tables for multilingual HR documents and feedback
Run this to add HRDocument and HRFeedback tables to existing database
"""
from database import engine, SessionLocal
from models import Base, HRDocument, HRFeedback
from sqlalchemy import inspect


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def create_new_tables():
    """Create new tables if they don't exist"""
    print("=" * 70)
    print("📊 CREATING NEW TABLES")
    print("=" * 70)
    
    # Check existing tables
    print("\n🔍 Checking existing tables...")
    hr_documents_exists = check_table_exists('hr_documents')
    hr_feedback_exists = check_table_exists('hr_feedback')
    
    if hr_documents_exists:
        print("  ✓ hr_documents table already exists")
    else:
        print("  ✗ hr_documents table not found - will create")
    
    if hr_feedback_exists:
        print("  ✓ hr_feedback table already exists")
    else:
        print("  ✗ hr_feedback table not found - will create")
    
    # Create tables
    if not hr_documents_exists or not hr_feedback_exists:
        print("\n🔨 Creating new tables...")
        try:
            # Create only the new tables
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    else:
        print("\n✅ All tables already exist!")
    
    # Verify tables
    print("\n📋 Current database tables:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in sorted(tables):
        print(f"  ✓ {table}")
    
    return True


def show_table_schema():
    """Show schema for new tables"""
    print("\n" + "=" * 70)
    print("📐 TABLE SCHEMAS")
    print("=" * 70)
    
    inspector = inspect(engine)
    
    # HRDocument schema
    if check_table_exists('hr_documents'):
        print("\n📄 hr_documents:")
        columns = inspector.get_columns('hr_documents')
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  - {col['name']}: {col['type']} {nullable}")
    
    # HRFeedback schema
    if check_table_exists('hr_feedback'):
        print("\n💬 hr_feedback:")
        columns = inspector.get_columns('hr_feedback')
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  - {col['name']}: {col['type']} {nullable}")


def seed_sample_multilingual_docs():
    """Add sample multilingual documents"""
    print("\n" + "=" * 70)
    print("🌱 SEEDING SAMPLE MULTILINGUAL DOCUMENTS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Check if sample docs already exist
        existing = db.query(HRDocument).first()
        if existing:
            print("⚠️  Sample documents already exist. Skipping...")
            return
        
        # Sample documents in different languages
        sample_docs = [
            HRDocument(
                title="Vacation Policy",
                content="Employees are entitled to 15 days of paid leave per year.",
                language="en"
            ),
            HRDocument(
                title="Политика отпусков",
                content="Сотрудники имеют право на 15 дней оплачиваемого отпуска в год.",
                language="ru"
            ),
            HRDocument(
                title="Ta'til siyosati",
                content="Xodimlar yiliga 15 kun to'langan ta'tilga ega.",
                language="uz"
            )
        ]
        
        db.add_all(sample_docs)
        db.commit()
        
        print(f"✅ Added {len(sample_docs)} sample documents")
        for doc in sample_docs:
            print(f"  {doc.language.upper()}: {doc.title}")
    
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    
    finally:
        db.close()


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create new multilingual tables")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed sample multilingual documents"
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Show table schemas"
    )
    
    args = parser.parse_args()
    
    # Create tables
    success = create_new_tables()
    
    if not success:
        print("\n❌ Failed to create tables")
        return
    
    # Show schema if requested
    if args.schema:
        show_table_schema()
    
    # Seed sample data if requested
    if args.seed:
        seed_sample_multilingual_docs()
    
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print("\nNew tables ready:")
    print("  📄 hr_documents - Multilingual HR documents with embeddings")
    print("  💬 hr_feedback - User feedback and ratings")
    print("\nSupported languages: 🇺🇿 Uzbek, 🇷🇺 Russian, 🇬🇧 English")


if __name__ == "__main__":
    main()
