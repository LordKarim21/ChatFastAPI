from sqlalchemy.orm import Session
from chat.db.models import User
from chat.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    user = User(username=user_create.username, password_hash=hashed_password, email=user_create.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
