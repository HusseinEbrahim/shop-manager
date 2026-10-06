from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user, require_owner
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/setup", response_model=schemas.UserResponse, status_code=201)
def create_first_owner(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).first() is not None:
        raise HTTPException(status_code=403, detail="Setup already completed")

    user = models.User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def read_me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    _owner: models.User = Depends(require_owner),
):
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = models.User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user