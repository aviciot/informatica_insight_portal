from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import DateTime
from datetime import datetime, timezone

Base = declarative_base()

role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_name", String, ForeignKey("roles.name")),
    Column("permission", String, ForeignKey("permissions.permission"))
)

class Role(Base):
    __tablename__ = "roles"
    name = Column(String, primary_key=True)
    permissions = relationship("Permission", secondary=role_permissions_table, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    permission = Column(String, primary_key=True)
    roles = relationship("Role", secondary=role_permissions_table, back_populates="permissions")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, ForeignKey("roles.name"))
    role_rel = relationship("Role")


class UserVisit(Base):
    __tablename__ = "user_visits"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    login_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    page = Column(String, nullable=True)  # Optional: track visited page
