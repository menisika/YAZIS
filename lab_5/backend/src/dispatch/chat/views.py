from fastapi import APIRouter

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.chat import service as chat_service
from src.dispatch.chat.flows import send_message_flow
from src.dispatch.chat.models import (
    ChatConversationListItem,
    ChatConversationRead,
    ChatRequest,
    ChatResponse,
)
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
def send_message(
    body: ChatRequest,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    return send_message_flow(
        db_session=db_session,
        user_id=current_user.id,
        conversation_id=body.conversation_id,
        message=body.message,
    )


@router.get("/conversations", response_model=list[ChatConversationListItem])
def list_conversations(current_user: CurrentUser, db_session: SessionDep):
    return chat_service.get_conversations(
        db_session=db_session, user_id=current_user.id
    )


@router.get("/conversations/{conversation_id}", response_model=ChatConversationRead)
def get_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    conv = chat_service.get_conversation_with_messages(
        db_session=db_session, conversation_id=conversation_id
    )
    if not conv:
        raise NotFoundError("Conversation not found")
    return conv


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    chat_service.delete_conversation(
        db_session=db_session,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    return {"ok": True}
