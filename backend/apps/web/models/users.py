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
    role = Column(String, default="pending")  # pending, user, admin
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
    role: str = "pending"
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
        role: str = "pending",
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
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserModel.model_validate(user)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Fetch a single user by primary key."""
        row = self.db.query(User).filter(User.id == user_id).first()
        return UserModel.model_validate(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Fetch a single user by email address (case-insensitive)."""
        row = (
            self.db.query(User)
            .filter(User.email == email.lower())
            .first()
        )
        return UserModel.model_validate(row) if row else None

    def get_users(self, skip: int = 0, limit: int = 50) -> List[UserModel]:
        """Return a paginated list of all users."""
        rows = self.db.query(User).offset(skip).limit(limit).all()
        return [UserModel.model_validate(r) for r in rows]

    def get_num_users(self) -> int:
        """Return total count of user rows."""
        return self.db.query(User).count()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_user_by_id(self, user_id: str, updated: dict) -> Optional[UserModel]:
        """Patch arbitrary fields on a user record."""
        updated["updated_at"] = int(time.time())
        self.db.query(User).filter(User.id == user_id).update(updated)
        self.db.commit()
        return self.get_user_by_id(user_id)

    def update_user_last_active_by_id(self, user_id: str) -> Optional[UserModel]:
        """Convenience method to refresh the last_active_at timestamp."""
        return self.update_user_by_id(
            user_id, {"last_active_at": int(time.time())}
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_user_by_id(self, user_id: str) -> bool:
        """Hard-delete a user row. Returns True on success."""
        deleted = self.db.query(User).filter(User.id == user_id).delete()
        self.db.commit()
        return deleted > 0
