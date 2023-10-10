from sqlalchemy import Table, Column, Float, ForeignKey, Integer, String, DATETIME
from sqlalchemy.orm import relationship

from .database import Base

# class UserBook(Base):
#     __tablename__ = "user_book"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     book_id = Column(Integer, ForeignKey("books.id"))

user_book = Table(
    "user_book",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # 定义与账本的多对多关系
    books = relationship("Book", secondary=user_book, back_populates="members")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    # 定义与账本的多对多关系
    members = relationship("User", secondary=user_book, back_populates="books")
    # 定义与记录的一对多关系
    records = relationship("Record", back_populates="book")


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, index=True)
    note = Column(String, default=None)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    add_by = Column(Integer, ForeignKey("users.id"), index=True)
    add_at = Column(DATETIME, index=True)

    book = relationship("Book", back_populates="records")
    category = relationship("Category", back_populates="records")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, index=True, default=None)
    icon = Column(Integer)
    cn_name = Column(String)
    en_name = Column(String)

    records = relationship("Record", back_populates="category")
