"""
Standalone seed script — run from the project root:

    GDEV_API_TOKEN=secret DATABASE_URL=postgresql://... python seed.py

The script creates all tables (if they do not already exist) and then
inserts sample records. It is safe to run multiple times: it skips
seeding when contracts already exist in the database.
"""

from app.database import SessionLocal, engine
from app import models
from app.seed import seed_db


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
        print("Done.")
    finally:
        db.close()
