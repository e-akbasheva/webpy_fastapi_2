from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base
from typing import Literal, List

import uuid
import datetime
from sqlalchemy import String, ForeignKey, Uuid, DateTime, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

ModelName = Literal["User", "Adv", "Role", "Right"]

user_role_relation = Table(
    "user_role_relation",
    Base.metadata,
    Column("user_id", ForeignKey("adv_user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True)
)

role_right_relation = Table(
    "role_right_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("right_id", ForeignKey("right.id"), primary_key=True)
)

class Right(Base):
    __tablename__ = "right"

    id: Mapped[int]=mapped_column(primary_key=True)
    write: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    read: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    only_own: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    model: Mapped[ModelName]=mapped_column(String(50), nullable=False)

class Role(Base):
    __tablename__ = "role"

    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(50), unique=True, nullable=False)
    
    rights: Mapped[List[Right]]=relationship(
        secondary=role_right_relation,
        lazy="joined"
    )

class User(Base):
    __tablename__ = "adv_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(70), nullable=False)

    tokens: Mapped[list["Token"]] = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    roles: Mapped[List[Role]] = relationship(
        secondary=user_role_relation,
        lazy="joined"
    )

class Token(Base):
    __tablename__ = "token"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        server_default=func.gen_random_uuid(),
        unique=True, 
        nullable=False
    )

    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("adv_user.id"))
    user: Mapped[User] = relationship(User, back_populates="tokens", lazy="joined")

    @property
    def to_dict(self):
        return {
            "id": self.id, 
            "token": str(self.token), 
            "creation_time": self.creation_time.isoformat()
        }
    
class Adv(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    #author = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("adv_user.id"))
    user: Mapped[User] = relationship(User, lazy="joined")

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.user.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }