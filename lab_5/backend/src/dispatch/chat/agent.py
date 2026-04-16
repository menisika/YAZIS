"""LangGraph AI fitness assistant agent using Functional API."""

from typing import Literal

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_groq import ChatGroq
from langgraph.graph import END, START, MessagesState, StateGraph
from sqlmodel import Session

from src.dispatch.chat.tools import create_assistant_tools
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

    def llm_call(state: MessagesState):
        return {
            "messages": [
                llm_with_tools.invoke(
                    [SystemMessage(content=ASSISTANT_SYSTEM_PROMPT)] + state["messages"]
                )
            ]
        }

    def tool_node(state: MessagesState):
        results = []
        for tool_call in state["messages"][-1].tool_calls:
            tool_fn = tools_by_name[tool_call["name"]]
            observation = tool_fn.invoke(tool_call["args"])
            results.append(
                ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
            )
        return {"messages": results}

    def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tool_node"
        return END

    graph = StateGraph(MessagesState)
    graph.add_node("llm_call", llm_call)
    graph.add_node("tool_node", tool_node)
    graph.add_edge(START, "llm_call")
    graph.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    graph.add_edge("tool_node", "llm_call")

    return graph.compile()


def run_assistant(
    db_session: Session,
    user_id: int,
    messages: list[BaseMessage],
) -> str:
    """Run the assistant agent with conversation history and return the response."""
    agent = create_assistant_agent(db_session, user_id)
    result = agent.invoke({"messages": messages})

    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content and not (hasattr(msg, "tool_calls") and msg.tool_calls):
            return msg.content

    return "I'm sorry, I couldn't process your request. Please try again."
