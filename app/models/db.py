from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime

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

def currentTimeFactory() -> str:
    return str(datetime.datetime.now(datetime.timezone.utc).timestamp())

class ChatSessionBase(SQLModel):
    title: str = Field(max_length=255)

class ChatSessionTable(ChatSessionBase, table=True):
    id: int | None = Field(default=None, primary_key=True) # Somehow it implies auto increment
    # INFO: This may be a explicit way to define auto increment
    # id: int | None = Field(default_factory=None, primary_key=True, sa_column_kwargs={'autoincrement': True}) 
    created_at: str = Field(default_factory=currentTimeFactory)

class ChatSessionPublic(ChatSessionBase):
    id: int

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
    id: int | None = Field(default=None, primary_key=True)
    created_at: str = Field(default_factory=currentTimeFactory)

    role: str = Field(max_length=12)
    session_id: int = Field(foreign_key="chatsessiontable.id", nullable=False)

class ChatMessagePublic(ChatMessageBase):
    id: int
    role: str
    session_id: int

class ChatMessageCreate(ChatMessageBase):
    session_id: int
    role: str = Field(max_length=12)