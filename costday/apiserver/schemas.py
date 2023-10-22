from typing import Union
from pydantic import BaseModel

from datetime import datetime


# 用户
class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


# token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


# 记录
class RecordBase(BaseModel):
    amount: float
    note: Union[str, None] = None
    category_id: int
    book_id: int
    type_: int = 1  # 1 expanse, 2 income


class RecordCreate(RecordBase):
    pass


class Record(RecordBase):
    id: int
    add_by: int
    add_at: datetime

    class Config:
        orm_mode = True


# 类别
class CategoryBase(BaseModel):
    parent_id: Union[int, None] = None
    icon: int
    cn_name: str
    en_name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


# 账本
class BookBase(BaseModel):
    name: str
    members: list[User]


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True


# 账本用户
class UserBookBase(BaseModel):
    user_id: int
    book_id: int


class UserBookCreate(UserBookBase):
    pass


class UserBook(UserBookBase):
    id: int

    class Config:
        orm_mode = True
