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
class ChatSession(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    # user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
