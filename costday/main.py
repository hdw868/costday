import logging
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status

from . import crud, models, schemas
from .auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .crud import authenticate_user, get_current_user
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def startup_event():
    db = SessionLocal()
    try:
        crud.add_predefined_users(db)
        crud.add_predefined_categories(db)
        crud.add_predefined_book(db)
        crud.add_predefined_user_book(db)
        crud.add_records_for_test(db)
    except IntegrityError:
        pass
    except Exception as e:
        logging.exception(e)
    finally:
        db.close()


app.add_event_handler("startup", startup_event)


@app.get("/")
async def greet():
    return {"message": "Hello, labor man!"}


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# records
@app.post("/records", response_model=schemas.Record, tags=["records"])
def create_record(
        record: schemas.RecordCreate, db: Session = Depends(get_db)
):
    return crud.create_user_record(db=db, record=record)


@app.get("/records", response_model=list[schemas.Record], tags=["records"])
async def read_records(book_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_records = crud.get_records(db, book_id=book_id, skip=skip, limit=limit)
    return db_records


@app.get("/records/{record_id}", response_model=schemas.Record, tags=["records"])
async def read_record(record_id, db: Session = Depends(get_db)):
    db_record = crud.get_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@app.put("/records/{record_id}", response_model=schemas.Record, tags=["records"])
async def update_record(record_id, record: schemas.RecordCreate, db: Session = Depends(get_db)):
    return crud.update_record(db, record_id, record)


@app.delete("/records/{record_id}", tags=["records"])
async def delete_record(record_id, db: Session = Depends(get_db)):
    return crud.delete_record(db, record_id)


# users
@app.post("/users", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_users = crud.get_users(db, skip=skip, limit=limit)
    return db_users


@app.get("/users/me", response_model=schemas.User, tags=["users"])
async def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user


@app.get("/users/{user_id}", response_model=schemas.User, tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User, tags=["users"])
def update_user(user_id, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, user)


# categories
@app.get("/categories", response_model=list[schemas.Category], tags=["categories"])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_categories = crud.get_categories(db, skip=skip, limit=limit)
    return db_categories


@app.get("/categories/{category_id}", response_model=schemas.Category, tags=["categories"])
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.post("/categories", response_model=schemas.Category, tags=["categories"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.create_category(db=db, category=category)
    return db_category


@app.put("/categories/{category_id}", response_model=schemas.Category, tags=["categories"])
def update_category(category_id, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.update_category(
        db=db, category_id=category_id, category=category)
    return db_category


@app.delete("/categories/{category_id}", tags=["categories"])
def delete_category(category_id, db: Session = Depends(get_db)):
    return crud.delete_category(db=db, category_id=category_id)


# books
@app.post("/books", response_model=schemas.Book, tags=["books"])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = crud.create_book(db=db, book=book)
    return db_book


@app.get("/books", response_model=list[schemas.Book], tags=["books"])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_books = crud.get_books(db, skip=skip, limit=limit)
    return db_books


@app.get("/books/{book_id}", response_model=schemas.Book, tags=["books"])
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", response_model=schemas.Book, tags=["books"])
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.update_book(db, book_id, book)


@app.delete("/books/{book_id}", tags=["books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)
