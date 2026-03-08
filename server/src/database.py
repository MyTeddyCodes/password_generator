from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    LargeBinary,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

""" DATABASE """


class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    login = Column(String, index=True)
    username = Column(String)
    password = Column(String)

    owner = relationship("User", back_populates="passwords")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, default=1)
    # The CheckConstraint ensures the id can ONLY be 1
    __table_args__ = (
        CheckConstraint(id == 1, name='only_one_row'),
    )
    # email = Column(String, unique=True)
    salt = Column(LargeBinary)  # 👈 SALT IS STORED HERE (not secret!)
    password_hash = Column(String)  # For authentication

    passwords = relationship(
        "Password", back_populates="owner", cascade="all, delete-orphan")
