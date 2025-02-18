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

    # # Relationship: One ChatSession -> Many ChatMessages
    # messages: List["ChatMessage"] = Relationship(back_populates="session")

    # # Relationship: Many ChatSessions -> One User
    # user: Optional[User] = Relationship(back_populates="chat_sessions")

# ==========================
# Chat Message Table
# ==========================
# class ChatMessage(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     session_id: UUID = Field(foreign_key="chatsession.id", nullable=False)
#     role: str = Field(max_length=20, regex="^(user|assistant)$")  # Constraint: 'user' or 'assistant'
#     content: str  # Fixed incorrect column type 'CONTENT' (should be 'TEXT' or 'str' in Python)
#     created_at: datetime = Field(default_factory=datetime.utcnow)

#     # Relationship: Many ChatMessages -> One ChatSession
#     session: ChatSession = Relationship(back_populates="messages")
