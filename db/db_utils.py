from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,text,delete, MetaData, Table
from sqlalchemy.exc import OperationalError
from db.models import Base, role_permissions_table, Role, User,Permission
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def test_db_connection():
    """Attempts to connect to the database using `get_db_engine()`."""
    try:
        engine = get_db_engine()  # Use the provided function
        with engine.connect():
            return "✅ Connection Successful!"
    except OperationalError as e:
        return f"❌ Connection Failed: {str(e)}"
    except ValueError as e:
        return f"⚠️ {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

def get_db_engine(config):
    """Return SQLAlchemy engine based on preferred database."""
    db_preference = config.get("dashboard_db.work_with")


    if db_preference == "sqlite":
        raw_path = config.get("dashboard_db.sqlite.db_path")
        db_path = Path(__file__).resolve().parent.parent / raw_path  # force path to project root
        os.makedirs(db_path.parent, exist_ok=True)
        return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    elif db_preference == "postgres":
        db_cfg = config.get("dashboard_db.postgres")
        return create_engine(
            f"postgresql://{db_cfg['user']}:{db_cfg['password']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['dbname']}",
            echo=False
        )

    else:
        raise ValueError(f"❌ Unsupported database preference: {db_preference}")

def get_db_session(config):
    """Get a new database session using provided config."""
    engine = get_db_engine(config)
    Session = sessionmaker(bind=engine)
    return Session()

def initialize_database(config):
    """Create all database tables if they don't exist."""
    engine = get_db_engine(config)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger.info("✅ Database tables initialized.")


