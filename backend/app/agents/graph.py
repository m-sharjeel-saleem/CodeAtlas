"""LangGraph wiring for CodeAtlas.

Flow:

    START → router → retriever ─┬─ "chat"/"architecture" → responder → END
                                └─ "review" → [security ‖ performance ‖ logic] → critic → END

For a review, the conditional edge returns a *list* of node names, so the three
reviewer agents fan out in parallel and append to `findings` via the state
reducer; the Critic then verifies each finding against the retrieved source.
"""
from langgraph.graph import END, START, StateGraph

from app.agents.nodes.critic import critic_node
from app.agents.nodes.indexer import responder_node
from app.agents.nodes.retriever import retriever_node
from app.agents.nodes.reviewer import (
    logic_review_node,
    performance_review_node,
    security_review_node,
)
from app.agents.nodes.router import router_node
from app.agents.state import AgentState


def fan_out(state: AgentState) -> list[str]:
    """Pick the node(s) to run after retrieval, based on intent."""
    if state.get("intent") == "review":
        return ["security", "performance", "logic"]
    return ["responder"]


def build_graph():
    """Compile and return the CodeAtlas agent graph."""
    g = StateGraph(AgentState)

    g.add_node("router", router_node)
    g.add_node("retriever", retriever_node)
    g.add_node("responder", responder_node)
    g.add_node("security", security_review_node)
    g.add_node("performance", performance_review_node)
    g.add_node("logic", logic_review_node)
    g.add_node("critic", critic_node)

    g.add_edge(START, "router")
    g.add_edge("router", "retriever")

    # Branch on intent: either a single responder, or the parallel review fan-out.
    g.add_conditional_edges(
        "retriever",
        fan_out,
        ["responder", "security", "performance", "logic"],
    )

    # All reviewers converge on the critic; the critic waits for all three.
    g.add_edge("security", "critic")
    g.add_edge("performance", "critic")
    g.add_edge("logic", "critic")

    g.add_edge("responder", END)
    g.add_edge("critic", END)

    return g.compile()


# Compiled once at import; reuse across requests.
graph = build_graph()
