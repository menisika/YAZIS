"""AI fitness assistant agent."""

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from sqlmodel import Session

from src.dispatch.chat.tools import create_assistant_tools
from src.dispatch.common.agent_graph import build_react_graph
from src.dispatch.config import settings

ASSISTANT_SYSTEM_PROMPT = """You are an expert fitness coach and nutritionist integrated into a workout app. You have access to the user's profile, workout plan, and recent activity through your tools.

Your capabilities:
- Answer questions about exercise technique, form, and variations
- Provide personalized nutrition advice based on the user's profile and goals
- Suggest workout adjustments based on how the user is feeling
- Help with recovery strategies (sleep, stretching, injury management)
- Explain the reasoning behind the workout plan

Guidelines:
- Always be encouraging and supportive
- If the user reports pain or injury, err on the side of caution and recommend rest or seeing a professional
- Base nutrition advice on the user's TDEE and goals
- Keep responses concise and actionable
- Use the tools to access user data before giving personalized advice
- If you don't know something medical, say so and recommend consulting a healthcare professional"""


def create_assistant_agent(db_session: Session, user_id: int):
    """Create a LangGraph AI assistant agent."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        api_key=settings.groq_api_key,
    )
    tools = create_assistant_tools(db_session, user_id)
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)
    return build_react_graph(llm_with_tools, tools_by_name, ASSISTANT_SYSTEM_PROMPT)


def run_assistant(
    db_session: Session,
    user_id: int,
    messages: list[BaseMessage],
) -> str:
    """Run the assistant agent with conversation history and return the response."""
    agent = create_assistant_agent(db_session, user_id)
    result = agent.invoke({"messages": messages})

    for msg in reversed(result["messages"]):
        if (
            hasattr(msg, "content")
            and isinstance(msg.content, str)
            and msg.content
            and not (hasattr(msg, "tool_calls") and msg.tool_calls)
        ):
            return msg.content

    return "I'm sorry, I couldn't process your request. Please try again."
