from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from schema.schemas import DaysDecision, AgentState
import os


def parse_input(state: AgentState) -> dict:
    cleaned_topic = state["topic"].strip()

    llm = ChatGroq(model_name="Llama-3.3-70B-Versatile", api_key=os.getenv("GROQ_API_KEY"))
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
        default_days = state.get("total_days") or 5
        total_days = max(3, min(14, default_days))
        print(f"[parse_input] LLM decision failed ({e}) — using {total_days} days")

    return {
        "topic": cleaned_topic,
        "total_days": total_days,
    }
