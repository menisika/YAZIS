"""LangGraph workout planner agent using Graph API."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, MessagesState, StateGraph
from sqlmodel import Session

from src.dispatch.config import settings
from src.dispatch.workout.tools import create_runtime_tools

WORKOUT_SYSTEM_PROMPT = """You are an expert fitness coach and workout planner. Your job is to create a personalized weekly workout plan.

Follow this process:
1. First, call get_user_profile_impl to understand the user's biometrics, fitness level, preferences, and injuries.
2. Call check_recovery_status_impl to see fatigue levels per muscle group from recent workouts.
3. Call get_recent_workout_history_impl to see what exercises were done recently (for variety).
4. Based on the user's workout_days_per_week, determine the split:
   - 3 days: Full Body A / Full Body B / Full Body C
   - 4 days: Upper / Lower / Upper / Lower
   - 5 days: Push / Pull / Legs / Upper / Lower
   - 6 days: Push / Pull / Legs / Push / Pull / Legs
5. For each training day, call get_exercise_catalog_impl with the target muscle groups to find exercises.
6. Select exercises following these rules:
   - Prioritize compound movements first (bench press, squat, deadlift, rows)
   - Avoid exercises for muscle groups with fatigue_score > 0.85
   - Avoid recently repeated exercises for variety
   - Match difficulty to user's fitness_level
   - Respect injury exclusions
   - Fill the target session_duration_min (~4 min per set including rest)
   - Weekly sets per muscle group: beginner 6-10, intermediate 10-16, advanced 16-22
7. Order exercises: compounds first, then isolation, then core/abs.
8. After building all days, call save_workout_plan_impl with the complete plan.

The days_json format for save_workout_plan_impl must be a JSON array like:
[
  {
    "day_of_week": 0,
    "focus": "Push",
    "order_index": 0,
    "exercises": [
      {"exercise_id": 1, "sets": 4, "reps_min": 6, "reps_max": 10, "rest_seconds": 120, "order_index": 0, "notes": null}
    ]
  }
]

Assign rest days to remaining days of the week. Do not include rest days in the plan.
Always respond with a summary of the generated plan after saving it."""


def create_workout_agent(db_session: Session, user_id: int):
    """Create a LangGraph workout generation agent with runtime tools."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=settings.groq_api_key,
    )

    tools = create_runtime_tools(db_session, user_id)
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

    def llm_call(state: MessagesState):
        return {
            "messages": [
                llm_with_tools.invoke(
                    [SystemMessage(content=WORKOUT_SYSTEM_PROMPT)] + state["messages"]
                )
            ]
        }

    def tool_node(state: MessagesState):
        from langchain_core.messages import ToolMessage

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


async def generate_workout_plan(
    db_session: Session,
    user_id: int,
    week_start: str,
    preferences: dict | None = None,
) -> str:
    """Run the workout generation agent and return the summary."""
    agent = create_workout_agent(db_session, user_id)

    prompt = f"Generate a personalized weekly workout plan starting from {week_start}."
    if preferences:
        if preferences.get("focus_muscle_groups"):
            prompt += f" Focus on these muscle groups: {', '.join(preferences['focus_muscle_groups'])}."
        if preferences.get("exclude_exercises"):
            prompt += f" Exclude exercise IDs: {preferences['exclude_exercises']}."

    messages = [HumanMessage(content=prompt)]
    result = agent.invoke({"messages": messages})

    # Return the last AI message
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and not hasattr(msg, "tool_calls"):
            return msg.content
        if hasattr(msg, "content") and hasattr(msg, "tool_calls") and not msg.tool_calls:
            return msg.content

    return "Workout plan generated successfully."
