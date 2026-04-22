"""Shared ReAct agent graph builder used by chat and other modules."""

from typing import Literal

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END, START, MessagesState, StateGraph


def build_react_graph(llm_with_tools, tools_by_name: dict, system_prompt: str):
    """Build and compile a standard ReAct (reason + act) LangGraph.

    Args:
        llm_with_tools: An LLM already bound with tools via llm.bind_tools(tools).
        tools_by_name: Mapping of tool_name -> tool callable.
        system_prompt: System message content injected before every LLM call.

    Returns:
        A compiled LangGraph ready for .invoke({"messages": [...]}).
    """

    def llm_call(state: MessagesState):
        return {
            "messages": [
                llm_with_tools.invoke(
                    [SystemMessage(content=system_prompt)] + state["messages"]
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
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tool_node"
        return END

    graph = StateGraph(MessagesState)
    graph.add_node("llm_call", llm_call)
    graph.add_node("tool_node", tool_node)
    graph.add_edge(START, "llm_call")
    graph.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    graph.add_edge("tool_node", "llm_call")

    return graph.compile()
