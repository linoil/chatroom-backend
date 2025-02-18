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

    # INFO: By cascade_delete=True, it will delete all related messages when the session is deleted
    # This behavior is performed by PYTHON
    messages: List["ChatMessageTable"] = Relationship(back_populates="session", cascade_delete=True)

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
    content: str = Field(max_length=5000)

class ChatMessageTable(ChatMessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: str = Field(default_factory=currentTimeFactory)

    role: str = Field(max_length=12)
    # INFO: By cascade_delete=True, this message will be deleted when the session is deleted
    # This behavior is performed by SQL
    session_id: int = Field(foreign_key="chatsessiontable.id", nullable=False, ondelete="CASCADE")

    session: ChatSessionTable = Relationship(back_populates="messages") 

class ChatMessagePublic(ChatMessageBase):
    id: int
    role: str

class ChatMessageCreate(ChatMessageBase):
    session_id: int
    role: str = Field(max_length=12)
