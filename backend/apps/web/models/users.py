"""User models and database operations for Open WebUI."""

from pydantic import BaseModel
from typing import Optional, List
import time
import uuid

from sqlalchemy import Column, String, Boolean, BigInteger, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """SQLAlchemy User table model."""

    __tablename__ = "user"

    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    # Changed default role to "user" so new sign-ups don't need manual approval
    role = Column(String, default="user")  # pending, user, admin
    profile_image_url = Column(Text, nullable=True)
    api_key = Column(String, nullable=True, unique=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    last_active_at = Column(BigInteger)
    is_active = Column(Boolean, default=True)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class UserModel(BaseModel):
    """Pydantic representation of a user record."""

    id: str
    name: str
    email: str
    # Mirror the DB default: new users start as "user" rather than "pending"
    role: str = "user"
    profile_image_url: Optional[str] = None
    api_key: Optional[str] = None
    created_at: int
    updated_at: int
    last_active_at: int
    is_active: bool = True

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Public-facing user data returned by API endpoints."""

    id: str
    name: str
    email: str
    role: str
    profile_image_url: Optional[str] = None
    created_at: int
    last_active_at: int


class UserUpdateForm(BaseModel):
    """Fields that a user is allowed to update on their own profile."""

    name: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserRoleUpdateForm(BaseModel):
    """Admin-only form for changing a user's role."""

    id: str
    role: str  # "pending" | "user" | "admin"


# ---------------------------------------------------------------------------
# Database access helpers
# ---------------------------------------------------------------------------


class UsersTable:
    """Thin wrapper around the User table providing CRUD helpers."""

    def __init__(self, db):
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def insert_new_user(
        self,
        name: str,
        email: str,
        role: str = "user",
        profile_image_url: Optional[str] = None,
    ) -> Optional[UserModel]:
        """Create a new user row and return the resulting model."""
        now = int(time.time())
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            role=role,
            profile_image_url=profile_image_url,
            created_at=now,
            updated_at=now,
            last_active_at=now,
        )
        self.db.add(
