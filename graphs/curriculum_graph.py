from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.messages import HumanMessage, SystemMessage
import os
import re
import sqlalchemy as sa
from schemas.schemas import (
    DaysDecision,
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


def parse_input(state: AgentState) -> dict:
    """
    Sanitise topic, then let the LLM decide the optimal number of days
    based on the topic's breadth and complexity.
    Falls back to user-provided total_days if LLM call fails.
    """
    cleaned_topic = state["topic"].strip()

    llm = ChatGroq(model_name="Llama-3.3-70B-Versatile", api_key=os.getenv("GROQ_API"))
    structured_llm = llm.with_structured_output(DaysDecision)

    try:
        decision: DaysDecision = structured_llm.invoke(
            [
                SystemMessage(
                    content="""You are a curriculum planner for a beginner learning newsletter.
Your job is to decide how many days a topic needs to be covered well — 
not too shallow, not overwhelming.

Guidelines:
- 3 days:  very focused, narrow topic (e.g. "what is a token", "how GPS works")
- 5 days:  clear single-domain topic (e.g. "how transformers work", "what is inflation")
- 7 days:  broader topic with multiple interconnected ideas (e.g. "how the internet works", "what is machine learning")
- 10 days: wide domain needing real depth (e.g. "the history of AI", "how financial markets work")
- 14 days: only for very broad domains a beginner needs significant time to absorb (e.g. "quantum computing", "evolutionary biology")

Always prefer fewer days. A tight 5-day arc beats a padded 10-day one."""
                ),
                HumanMessage(
                    content=f"""
Topic: "{cleaned_topic}"

How many days does this topic need for a complete beginner to genuinely understand it?
Stay between 3 and 14 days.
"""
                ),
            ]
        )

        total_days = decision.total_days
        print(f"[parse_input] topic='{cleaned_topic}' → {total_days} days")

    except Exception as e:
        # Fall back to user-provided value, clamped to safe range
        total_days = max(3, min(14, state.get("total_days", 5)))
        print(f"[parse_input] LLM decision failed ({e}) — using {total_days} days")

    return {
        "topic": cleaned_topic,
        "total_days": total_days,
    }


def generate_syllabus(state: AgentState) -> dict:
    structured_llm = llm.with_structured_output(SyllabusOutput)
    response: SyllabusOutput = structured_llm.invoke(
        [
            SystemMessage(
                content="""You are an expert curriculum designer 
        specialising in beginner-friendly conceptual learning paths.
        You MUST return the response using the provided tool schema.
        The output must contain a field called `syllabus`.
        
        Your curriculum is purely theoretical — no setup, no coding, no tools.
        Every concept should be something the reader understands deeply,
        not something they do or install."""
            ),
            HumanMessage(
                content=f"""
Design a {state['total_days']}-day conceptual learning curriculum for: "{state['topic']}"
Target level: complete beginner — no prior knowledge assumed

Rules:
1. Day 1 must explain what {state['topic']} is, where it came from, and why it matters
2. Each day must introduce exactly 3–4 concepts
3. Concepts must be ideas, mental models, or principles — never tasks or actions
4. Concepts must build logically from previous days
5. Day {state['total_days']} must synthesise everything — how the concepts connect and what the bigger picture looks like
6. Titles should spark curiosity, not sound like a course syllabus
7. Never include: installation, setup, coding, tools, frameworks, or hands-on tasks
8. For each day write a description: 2–3 sentences in second-person ("You'll discover…",  ← NEW
   "By the end of today…") that tease what the reader will learn. Be specific —
   never write "We cover the basics." or "An introduction to X."
"""
            ),
        ]
    )

    print(f"[generate_syllabus] Generated {len(response.syllabus)} days")
    return {"syllabus": [s.model_dump() for s in response.syllabus]}


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
