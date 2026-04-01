from langchain_groq import ChatGroq
from schema.schemas import ContentState, ConceptBrief
from prompts.prompt import SUMMARIZER_PROMPT
import os


def summarizer_node(state: ContentState) -> dict:
    print(f"\n{'='*60}")
    print("📝 SUMMARIZER NODE")
    print(f"{'='*60}")

    plan = state["plan"]
    research = state["research"]

    print(f"📋 Total raw results: {len(research)}")

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

    results_per_concept = len(research) // len(plan.sections)

    briefs = []
    for i, section in enumerate(plan.sections):
        start = i * results_per_concept
        end = start + results_per_concept
        concept_results = research[start:end]

        print(f"\n🔎 Distilling: '{section.concept}' ({len(concept_results)} results)")

        raw_results = "\n\n".join(
            [
                f"Title: {r.title}\nURL: {r.url}\nSummary: {r.summary[:900]}\nSnippet: {r.snippet[:600]}"
                for r in concept_results
            ]
        )

        prompt = SUMMARIZER_PROMPT.format(
            concept=section.concept, raw_results=raw_results
        )

        brief = llm.with_structured_output(ConceptBrief).invoke(prompt)
        briefs.append(brief)

        print(f"   ✅ Definition: {brief.definition[:80]}...")
        print(f"   💡 Fun fact:   {brief.fun_fact[:80]}...")
        print(f"   🔗 Best URL:   {brief.best_url}")

    print(f"\n{'='*60}")
    print(f"✅ Summarization complete — {len(briefs)} concept briefs ready")
    print(f"{'='*60}\n")

    return {"research_summary": briefs}
