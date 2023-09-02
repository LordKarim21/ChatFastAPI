from pydantic import BaseModel
from datetime import datetime
from typing import List


class MessageCreate(BaseModel):
    sender: str
    content: str


class Message(MessageCreate):
    id: int
    timestamp: datetime


class UserCreate(BaseModel):
    username: str
    password: str


class User(UserCreate):
    id: int


class ChatCreate(BaseModel):
    name: str


class Chat(ChatCreate):
    id: int
    participants: List[User]


class ChatParticipantCreate(BaseModel):
    user_id: int
    chat_id: int


class ChatParticipant(ChatParticipantCreate):
    id: int
