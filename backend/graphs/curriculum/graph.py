from langgraph.graph import StateGraph, START, END
from schema.schemas import AgentState
from graphs.curriculum.nodes.parse_input import parse_input
from graphs.curriculum.nodes.generate_syllabus import generate_syllabus
from graphs.curriculum.nodes.save_to_db import save_to_db


def build_curriculum_graph():
    g = StateGraph(AgentState)

    g.add_node("parse_input", parse_input)
    g.add_node("generate_syllabus", generate_syllabus)
    g.add_node("save_to_db", save_to_db)

    g.add_edge(START, "parse_input")
    g.add_edge("parse_input", "generate_syllabus")
    g.add_edge("generate_syllabus", "save_to_db")
    g.add_edge("save_to_db", END)

    return g.compile()
