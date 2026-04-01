from langchain_groq import ChatGroq
from schema.schemas import ContentState, CriticOutput
from prompts.prompt import CRITIC_PROMPT
import os


def critic_node(state: ContentState) -> ContentState:
    print(f"\n{'='*60}")
    print(f"🔍 CRITIC NODE")
    print(f"{'='*60}")

    revision_count = state.get("revision_count", 0)

    if revision_count >= 3:
        print(f"   ⚠️ Max revisions reached — auto approving")
        return {"approved": True, "feedbacks": []}

    research_text = ""
    for brief in state["research_summary"]:
        research_text += f"""
    ---
    Concept: {brief.concept}
    Definition: {brief.definition}
    Real World Example: {brief.example}
    Fun Fact: {brief.fun_fact}
    Best URL: {brief.best_url}
    ---
    """
    prompt = CRITIC_PROMPT.format(
        draft=state["draft"], research_summaries=research_text
    )
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    result: CriticOutput = llm.with_structured_output(CriticOutput).invoke(prompt)

    for annotation in result.feedbacks:
        print(f"   ⚠️  [{annotation.section}] {annotation.issue[:80]}...")

    print(f"   ✅ Approved: {result.approved}")
    print(f"{'='*60}\n")

    return {
        "feedbacks": result.feedbacks,
        "approved": result.approved,
        "revision_count": revision_count + 1,
    }


def should_revise(state: ContentState) -> str:
    if state["approved"]:
        return "end"
    if state["revision_count"] >= 3:
        return "end"
    return "writer"
