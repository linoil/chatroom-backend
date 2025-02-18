from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

# # ==========================
# # User Table
# # ==========================
# class User(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     name: str = Field(max_length=100)
#     email: str = Field(max_length=255, unique=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)

#     # Relationship: One User -> Many ChatSessions
#     chat_sessions: List["ChatSession"] = Relationship(back_populates="user")


# ==========================
# Chat Session Table
# ==========================

class ChatSessionBase(SQLModel):
    title: str = Field(max_length=255)

class ChatSessionTable(ChatSessionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSessionPublic(ChatSessionBase):
    id: UUID

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)


# ==========================
# Chat Message Table
# ==========================
class ChatMessageBase(SQLModel):
    content: str = Field(max_length=1000)

class ChatMessageTable(ChatMessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    role: str = Field(max_length=12, regex="^(user|assistant)$")
    session_id: UUID = Field(foreign_key="chatsessiontable.id", nullable=False)

class ChatMessagePublic(ChatMessageBase):
    id: UUID
    role: str
    session_id: UUID

class ChatMessageCreate(ChatMessageBase):
    session_id: UUID
    role: str = Field(max_length=12, regex="^(user|assistant)$")