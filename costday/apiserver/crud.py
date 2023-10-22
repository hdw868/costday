from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from . import models, schemas, auth
from .auth import verify_password, oauth2_scheme, SECRET_KEY, ALGORITHM
from .schemas import TokenData


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(db: Session, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email, username=user.username, hashed_password=auth.get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()


def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = get_user(db, user_id)
    if db_user:
        db_user = db_user.update(user.dict())
        db.commit()
        return db_user


def get_record(db: Session, record_id: int):
    return db.query(models.Record).filter(models.Record.id == record_id).first()


def get_records(db: Session, book_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Record).filter(models.Record.book_id == book_id).offset(skip).limit(limit).all()


def create_user_record(db: Session, record: schemas.RecordCreate, user_id: int):
    db_record = models.Record(**record.dict(), add_by=user_id, add_at=datetime.now())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, record_id: int):
    db_record = get_record(db, record_id)
    if db_record:
        db.delete(db_record)
        db.commit()


def update_record(db: Session, record_id: int, record: schemas.RecordCreate):
    db_record = get_record(db, record_id)
    if db_record:
        db_record = db_record.update(record.dict())
        db.commit()
        return db_record


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()


def update_category(db: Session, category_id: int, category: schemas.CategoryCreate):
    db_category = get_category(db, category_id)
    if db_category:
        db_category = db_category.update(category.dict())
        db.commit()
        return db_category


def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = get_book(db, book_id)
    if db_book:
        db_book = db_book.update(book.dict())
        db.commit()
        return db_book


def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book:
        db.delete(db_book)
        db.commit()


def create_user_book(db: Session, user_book: schemas.UserBookCreate):
    db.execute(
        models.user_book.insert().values(user_id=user_book.user_id, book_id=user_book.book_id)
    )
    db.commit()
    return user_book


def add_predefined_categories(db: Session):
    predefined_categories = [
        {"cn_name": "购物", "en_name": "Shop", "icon": 1},
        {"cn_name": "服饰", "en_name": "Dress", "icon": 2},
        {"cn_name": "护肤", "en_name": "Necessity", "icon": 3},
        {"cn_name": "数码", "en_name": "Digital", "icon": 4},
        {"cn_name": "应用", "en_name": "App", "icon": 5},
        {"cn_name": "交通", "en_name": "Traffic", "icon": 6},
        {"cn_name": "旅行", "en_name": "Travel", "icon": 7},
        {"cn_name": "美食", "en_name": "Food", "icon": 8},
        {"cn_name": "娱乐", "en_name": "Entertainment", "icon": 9},
        {"cn_name": "游戏", "en_name": "Game", "icon": 91, "parent_id": 9},
        {"cn_name": "电影", "en_name": "Movie", "icon": 92, "parent_id": 9},
        {"cn_name": "生活", "en_name": "Life", "icon": 10},
        {"cn_name": "其他", "en_name": "Others", "icon": 11}
    ]

    for category_data in predefined_categories:
        category_create = schemas.CategoryCreate(**category_data)
        create_category(db=db, category=category_create)


def add_predefined_users(db: Session):
    predefined_users = [
        {"email": "admin@126.com", "username": "admin", "password": "admin"},
        {"email": "test@126.com", "username": "test", "password": "test"}
    ]
    for user_data in predefined_users:
        user_create = schemas.UserCreate(**user_data)
        create_user(db=db, user=user_create)


def add_predefined_book(db: Session):
    predefined_books = [
        {"name": "default", "members": []},
    ]
    for book_data in predefined_books:
        book_create = schemas.BookCreate(**book_data)
        create_book(db=db, book=book_create)


def add_predefined_user_book(db: Session):
    predefined_user_books = [
        {"user_id": 1, "book_id": 1},
        {"user_id": 2, "book_id": 1},
    ]
    for user_book_data in predefined_user_books:
        user_book_create = schemas.UserBookCreate(**user_book_data)
        create_user_book(db=db, user_book=user_book_create)


def add_records_for_test(db: Session):
    test_records = [
        {"amount": 100, "note": "test", "category_id": 1, "book_id": 1},
        {"amount": 20, "category_id": 1, "book_id": 1},
        {"amount": 70.2, "category_id": 2, "book_id": 1},
        {"amount": 10.5, "note": "test", "category_id": 3, "book_id": 1},
    ]
    for record in test_records:
        record_create = schemas.RecordCreate(**record)
        create_user_record(db=db, record=record_create, user_id=1)
