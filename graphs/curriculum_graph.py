from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
import re
import sqlalchemy as sa
from schemas.schemas import (
    SyllabusItem,
    AgentState,
    Source,
    FilteredSources,
    SyllabusOutput,
)
from db.database import init_db, SessionLocal
from db.crud import create_track, save_syllabus

load_dotenv()
init_db()


llm = ChatGroq(model_name="Llama-3.3-70B-Versatile", api_key=os.getenv("GROQ_API"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def parse_input(state: AgentState) -> AgentState:
    cleaned_topic = state["topic"].strip()
    clamped_days = max(3, min(60, state["total_days"]))
    return {"topic": cleaned_topic, "total_days": clamped_days}


def generate_syllabus(state: AgentState) -> dict:
    sources_text = "\n\n".join(
        f"[Source {i+1}] {s['title']}\nURL: {s['url']}\n{s['content']}"
        for i, s in enumerate(state["filtered_sources"])
    )
    structured_llm = llm.with_structured_output(SyllabusOutput)
    response: SyllabusOutput = structured_llm.invoke(
        [
            SystemMessage(
                content=(
                    """You are an expert curriculum designer specialising in beginner-friendly learning paths.\nYou MUST return the response using the provided tool schema.\nThe output must contain a field called `syllabus`."""
                )
            ),
            HumanMessage(
                content=f"""
Design a {state['total_days']}-day learning curriculum for: "{state['topic']}"
Target level: beginner

Use these research sources as context:
{sources_text}

Rules:
1. Day 1 must explain what {state['topic']} is and why it matters
2. Each day must introduce exactly 2–4 concepts
3. Concepts must build logically from previous days
4. Day {state['total_days']} must be a capstone ("putting it all together")
5. Titles should be curiosity-driven and engaging
"""
            ),
        ]
    )
    syllabus = response.syllabus
    print(f"[generate_syllabus] Generated {len(syllabus)} days")
    return {"syllabus": [s.model_dump() for s in syllabus]}


def save_to_db(state: AgentState) -> dict:
    """
    Creates a Track row and saves all SyllabusItems to SQLite.
    Returns track_id so downstream systems (Graph 2) can reference it.
    """
    db = SessionLocal()
    try:
        # Create the track
        track = create_track(
            db=db,
            topic=state["topic"],
            total_days=state["total_days"],
        )

        # Save every syllabus item
        save_syllabus(
            db=db,
            track_id=track.id,
            syllabus=state["syllabus"],  # already list[dict] from model_dump()
        )

        print(f"[save_to_db] Track {track.id} saved — {len(state['syllabus'])} days")
        return {"track_id": track.id}

    except Exception as e:
        db.rollback()
        print(f"[save_to_db] Failed: {e}")
        raise
    finally:
        db.close()


def build_curriculum_graph():
    g = StateGraph(AgentState)

    # nodes
    g.add_node("parse_input", parse_input)
    g.add_node("generate_syllabus", generate_syllabus)
    g.add_node("save_to_db", save_to_db)

    # edges (connections)
    g.add_edge(START, "parse_input")
    g.add_edge("parse_input", "generate_syllabus")
    g.add_edge("generate_syllabus", "save_to_db")
    g.add_edge("save_to_db", END)

    # Optionally, return or use the graph
    return g.compile()


if __name__ == "__main__":
    curriculum_graph = build_curriculum_graph()
    test_state = {
        "topic": "Diet plan of Peri meno pausal women",
        "total_days": 5,
        "syllabus": [],
        "revision_count": 0,
        "quality_score": 0.0,
    }
    result = curriculum_graph.invoke(test_state)
    print(result["syllabus"])
