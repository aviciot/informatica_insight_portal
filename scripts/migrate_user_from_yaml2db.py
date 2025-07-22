# scripts/migrate_from_yaml.py

from pathlib import Path
from config.config import Config
from db.models import Base, User, Role, Permission
from db.db_utils import get_db_engine, get_db_session, initialize_database
from sqlalchemy import text

# Load config from YAML
config_path = Path(__file__).resolve().parent.parent / "config" / "config.yaml"
config = Config(config_path)

# Initialize tables if they don't exist
initialize_database(config)


# Get engine and session based on config (SQLite or Postgres)
engine = get_db_engine(config)
session = get_db_session(config)

# Debug: Print existing table names
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        if config.get("dashboard_db.work_with") == "postgres"
        else "SELECT name FROM sqlite_master WHERE type='table';"
    ))
    print("Tables in DB:", [row[0] for row in result])

# Insert roles and permissions
for role_name, perms in config.get("role_permissions", {}).items():
    role_obj = session.get(Role, role_name)
    if not role_obj:
        role_obj = Role(name=role_name)
        session.add(role_obj)

    for perm in perms:
        perm_obj = session.get(Permission, perm)
        if not perm_obj:
            perm_obj = Permission(permission=perm)
            session.add(perm_obj)

        if perm_obj not in role_obj.permissions:
            role_obj.permissions.append(perm_obj)

# Insert users
for username, details in config.get("users", {}).items():
    user = session.query(User).filter_by(username=username).first()
    if not user:
        new_user = User(
            username=username,
            password=details["password"],  # assumed hashed already
            role=details["role"]
        )
        session.add(new_user)

session.commit()

# Debug counts
print("Inserted roles:", session.query(Role).count())
print("Inserted permissions:", session.query(Permission).count())
print("Inserted users:", session.query(User).count())

session.close()
print("✅ Migration completed successfully.")
