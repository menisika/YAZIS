"""Context assembly and chat flow orchestration."""

from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from src.dispatch.chat import service as chat_service
from src.dispatch.chat.agent import run_assistant
from src.dispatch.chat.models import ChatMessageRead, ChatResponse


def send_message_flow(
    *,
    db_session: Session,
    user_id: int,
    conversation_id: int | None,
    message: str,
) -> ChatResponse:
    """Full chat flow: manage conversation, build history, run agent, save response."""

    # Create or get conversation
    if conversation_id is None:
        conv = chat_service.create_conversation(
            db_session=db_session,
            user_id=user_id,
            title=message[:50],
        )
        conversation_id = conv.id

    # Save user message
    chat_service.add_message(
        db_session=db_session,
        conversation_id=conversation_id,
        role="user",
        content=message,
    )

    # Build message history for the agent
    recent = chat_service.get_recent_messages(
        db_session=db_session, conversation_id=conversation_id, limit=20
    )
    langchain_messages = []
    for msg in recent:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))

    # Run the LangGraph assistant agent
    response_text = run_assistant(
        db_session=db_session,
        user_id=user_id,
        messages=langchain_messages,
    )

    # Save assistant response
    assistant_msg = chat_service.add_message(
        db_session=db_session,
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageRead(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            created_at=assistant_msg.created_at,
        ),
    )
