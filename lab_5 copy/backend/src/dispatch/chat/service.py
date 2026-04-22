"""Conversation CRUD and history management."""

from sqlmodel import Session, func, select

from src.dispatch.chat.models import (
    ChatConversation,
    ChatConversationListItem,
    ChatConversationRead,
    ChatMessage,
    ChatMessageRead,
)
from src.dispatch.exceptions import NotFoundError


def get_conversation(*, db_session: Session, conversation_id: int) -> ChatConversation | None:
    return db_session.get(ChatConversation, conversation_id)


def get_conversations(*, db_session: Session, user_id: int) -> list[ChatConversationListItem]:
    stmt = (
        select(ChatConversation)
        .where(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.created_at.desc())
    )
    conversations = db_session.exec(stmt).all()
    result = []
    for c in conversations:
        count_stmt = select(func.count(ChatMessage.id)).where(ChatMessage.conversation_id == c.id)
        msg_count = db_session.exec(count_stmt).one()
        result.append(ChatConversationListItem(
            id=c.id, title=c.title, created_at=c.created_at, message_count=msg_count,
        ))
    return result


def get_conversation_with_messages(*, db_session: Session, conversation_id: int) -> ChatConversationRead | None:
    conv = get_conversation(db_session=db_session, conversation_id=conversation_id)
    if not conv:
        return None
    msgs_stmt = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    messages = db_session.exec(msgs_stmt).all()
    return ChatConversationRead(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        messages=[ChatMessageRead(**m.model_dump()) for m in messages],
    )


def create_conversation(*, db_session: Session, user_id: int, title: str | None = None) -> ChatConversation:
    conv = ChatConversation(user_id=user_id, title=title)
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)
    return conv


def add_message(*, db_session: Session, conversation_id: int, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(conversation_id=conversation_id, role=role, content=content)
    db_session.add(msg)
    db_session.commit()
    db_session.refresh(msg)
    return msg


def get_recent_messages(*, db_session: Session, conversation_id: int, limit: int = 20) -> list[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(db_session.exec(stmt).all())
    messages.reverse()  # Chronological order
    return messages


def delete_conversation(*, db_session: Session, conversation_id: int, user_id: int) -> bool:
    conv = get_conversation(db_session=db_session, conversation_id=conversation_id)
    if not conv or conv.user_id != user_id:
        raise NotFoundError("Conversation not found")
    db_session.delete(conv)
    db_session.commit()
    return True
