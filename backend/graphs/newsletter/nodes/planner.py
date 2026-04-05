from langchain_groq import ChatGroq
from schema.schemas import ContentState, Plan
from prompts.prompt import PLANNER_PROMPT
import os


def planner_node(state: ContentState) -> dict:
    prompt = PLANNER_PROMPT.format(
        day=state["item"]["day"],
        title=state["item"]["title"],
        concepts=", ".join(state["item"]["concepts"]),
    )
    llm = ChatGroq(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct", api_key=os.getenv("GROQ_API_KEY")
    )
    plan = llm.with_structured_output(Plan).invoke(prompt)

    return {"plan": plan}
