from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

# --- SQLModel Tables ---


class ChatConversation(SQLModel, table=True):
    __tablename__ = "chat_conversation"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["ChatMessage"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_message"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="chat_conversation.id", index=True, ondelete="CASCADE")
    role: str  # user / assistant / system
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: ChatConversation | None = Relationship(back_populates="messages")


# --- Pydantic Schemas ---


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: int
    message: ChatMessageRead


class ChatConversationRead(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    messages: list[ChatMessageRead] = []


class ChatConversationListItem(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    message_count: int = 0
