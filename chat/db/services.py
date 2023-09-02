from fastapi import HTTPException
from sqlalchemy.orm import Session
from chat.db.models import User, Message, Chat, ChatParticipant
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import List


SECRET_KEY = "your-secret-key"  # Замените на свой секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Получение информации о пользователе по username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Получение информации о пользователе по ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# Создание токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Система аутентификации
async def get_current_user(token: str, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="User not authenticated")
        user = get_user(db, username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        pass


# Создание сообщения
def create_message(db: Session, message_create: MessageCreate):
    message = Message(**message_create.dict(), timestamp=datetime.utcnow())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


# Получение сообщений для чата
def get_messages_for_chat(db: Session, chat_id: int) -> List[Message]:
    return db.query(Message).filter(Message.chat_id == chat_id).all()


# Создание пользователя
def create_user(db: Session, user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    user = User(username=user_create.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Создание чата
def create_chat(db: Session, chat_create: ChatCreate, current_user: User):
    chat = Chat(**chat_create.dict())
    db.add(chat)
    db.commit()

    # Добавление текущего пользователя в чат как участника
    chat_participant = ChatParticipant(user_id=current_user.id, chat_id=chat.id)
    db.add(chat_participant)
    db.commit()

    return chat


# Получение чатов пользователя
def get_chats_for_user(db: Session, user: User) -> List[Chat]:
    return db.query(Chat).join(ChatParticipant).filter(ChatParticipant.user_id == user.id).all()


# Добавление пользователя в чат
def create_chat_participant(db: Session, chat_participant_create: ChatParticipantCreate, current_user: User):
    chat_participant = ChatParticipant(**chat_participant_create.dict())
    db.add(chat_participant)
    db.commit()
    return chat_participant


# Получение участников чата для пользователя
def get_chat_participants_for_user(db: Session, user: User, chat_id: int) -> List[ChatParticipant]:
    return db.query(ChatParticipant).filter(ChatParticipant.user_id == user.id, ChatParticipant.chat_id == chat_id).all()
