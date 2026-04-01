from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from schema.schemas import SyllabusOutput, AgentState
import os


def generate_syllabus(state: AgentState) -> dict:
    llm = ChatGroq(model_name="Llama-3.3-70B-Versatile", api_key=os.getenv("GROQ_API"))
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
8. For each day write a description: 2–3 sentences in second-person ("You'll discover…",
   "By the end of today…") that tease what the reader will learn. Be specific —
   never write "We cover the basics." or "An introduction to X."
"""
            ),
        ]
    )

    print(f"[generate_syllabus] Generated {len(response.syllabus)} days")
    return {"syllabus": [s.model_dump() for s in response.syllabus]}
