from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from operator import add
from typing import Literal
from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.func import entrypoint
from langgraph.store.base import BaseStore

from tools_setup import model_with_tools, tools_by_name


# -------------------------
# State
# -------------------------
class AgentState(TypedDict):
    messages: Annotated[list, add]
    llm_calls: int


# -------------------------
# LLM Node
# -------------------------
def llm_call(state: AgentState):
    response = model_with_tools.invoke(
        [SystemMessage(content="You are a helpful assistant that solves arithmetic problems using tools when needed.")]
        + state["messages"]
    )

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# -------------------------
# Tool Node
# -------------------------
def tool_node(state: AgentState):
    last = state["messages"][-1]
    results = []

    for call in last.tool_calls:
        tool = tools_by_name[call["name"]]
        observation = tool.invoke(call["args"])

        results.append(
            ToolMessage(
                content=str(observation),
                tool_call_id=call["id"]
            )
        )

    return {"messages": results}


# -------------------------
# Routing
# -------------------------
def should_continue(state: AgentState) -> Literal["approve", END]:
    last = state["messages"][-1]

    if getattr(last, "tool_calls", None) and last.tool_calls:
        return "approve"

    return END


# -------------------------
# Approval Node (HITL)
# -------------------------
def approve_node(state: AgentState) -> Command:
    decision = interrupt({
        "question": "Approve tool execution?",
        "tool_calls": state["messages"][-1].tool_calls
    })

    return Command(goto="tool_node" if decision else END)


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(AgentState)

checkpointer = InMemorySaver()

builder.add_node("llm_call", llm_call)
builder.add_node("approve", approve_node)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["approve", END])
builder.add_edge("tool_node", "llm_call")

agent = builder.compile(checkpointer=checkpointer)


# -------------------------
# MAIN EXECUTION
# -------------------------
if __name__ == "__main__":

    config = {"configurable": {"thread_id": "thread-1"}}

    # -------------------------
    # RUN 1
    # -------------------------
    result = agent.invoke(
        {"messages": [HumanMessage(content="Add 3 and 4.")], "llm_calls": 0},
        config=config
    )

    print("Interrupt payload:", result.get("__interrupt__"))

    # -------------------------
    # RESUME (approve)
    # -------------------------
    resume = agent.invoke(Command(resume=True), config=config)
    print("Done:", resume["messages"][-1])


    # -------------------------
    # REJECT EXAMPLE
    # -------------------------
    config_reject = {"configurable": {"thread_id": "thread-2"}}

    result2 = agent.invoke(
        {"messages": [HumanMessage(content="Multiply 30 and 41.")], "llm_calls": 0},
        config=config_reject
    )

    print("Interrupt payload:", result2.get("__interrupt__"))

    resume2 = agent.invoke(Command(resume=False), config=config_reject)
    print("Rejected result:", resume2["messages"][-1])


    # -------------------------
    # FORK (state modification)
    # -------------------------
    history = list(agent.get_state_history(config_reject))

    picked = history[1]

    new_config = agent.update_state(
        picked.config,
        values={
            "messages": [HumanMessage(content="Multiply 30 and 41.")],
            "llm_calls": 0
        }
    )

    forked = agent.invoke(None, new_config)

    print("Forked result:", forked)