from langgraph.graph import StateGraph, START, END
from schema.schemas import ContentState
from graphs.newsletter.nodes.planner import planner_node
from graphs.newsletter.nodes.research import research_node
from graphs.newsletter.nodes.summarizer import summarizer_node
from graphs.newsletter.nodes.writer import writer_node
from graphs.newsletter.nodes.critic import critic_node, should_revise
from graphs.newsletter.nodes.finalizer import finalizer_node


def build_graph():
    g = StateGraph(ContentState)

    g.add_node("planner_node", planner_node)
    g.add_node("research_node", research_node)
    g.add_node("summarizer_node", summarizer_node)
    g.add_node("writer_node", writer_node)
    g.add_node("critic_node", critic_node)
    g.add_node("finalizer_node", finalizer_node)

    g.add_edge(START, "planner_node")
    g.add_edge("planner_node", "research_node")
    g.add_edge("research_node", "summarizer_node")
    g.add_edge("summarizer_node", "writer_node")
    g.add_edge("writer_node", "critic_node")
    g.add_conditional_edges(
        "critic_node",
        should_revise,
        {
            "writer": "writer_node",
            "end": "finalizer_node",
        },
    )
    g.add_edge("finalizer_node", END)

    return g.compile()
