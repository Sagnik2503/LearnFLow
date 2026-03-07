from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# SQLite for now — swap this one line for Supabase later:
# DATABASE_URL = "postgresql://user:password@db.supabase.co:5432/postgres"
DATABASE_URL = "sqlite:///./learnflow.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # needed for SQLite only, remove for Postgres
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """Creates all tables. Call once at startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yields a session. Use as a dependency in FastAPI or call directly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
