import os
import sys

# Add parent directory to path to enable local app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import Base, engine, SessionLocal
    from app.models.employee import Employee
    from seed import seed_database
except ModuleNotFoundError:
    from backend.app.database import Base, engine, SessionLocal
    from backend.app.models.employee import Employee
    from backend.seed import seed_database

from sqlalchemy import select, func

def main():
    print("Checking database status...")
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        count = db.scalar(select(func.count(Employee.id))) or 0
        if count == 0:
            print("Database is empty. Running seeding routine...")
            seed_database()
        else:
            print(f"Database already populated ({count} employees found). Skipping seed.")
    except Exception as e:
        print(f"Database empty check failed, attempting to seed: {e}")
        try:
            seed_database()
        except Exception as seed_err:
            print(f"Seeding failed: {seed_err}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
