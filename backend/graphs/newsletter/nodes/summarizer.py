from langchain_groq import ChatGroq
from schema.schemas import ContentState, ConceptBrief
from prompts.prompt import SUMMARIZER_PROMPT
import os


def summarizer_node(state: ContentState) -> dict:
    print(f"\n{'=' * 60}")
    print("📝 SUMMARIZER NODE")
    print(f"{'=' * 60}")

    plan = state["plan"]
    research = state["research"]

    print(f"📋 Total raw results: {len(research)}")

    llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", api_key=os.getenv("GROQ_API_KEY"))

    base_count = len(research) // len(plan.sections)
    remainder = len(research) % len(plan.sections)

    briefs = []
    offset = 0
    for i, section in enumerate(plan.sections):
        count = base_count + (1 if i < remainder else 0)
        concept_results = research[offset : offset + count]
        offset += count

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
        if brief.additional_urls:
            print(f"   📚 Additional: {len(brief.additional_urls)} extra URLs")

    print(f"\n{'=' * 60}")
    print(f"✅ Summarization complete — {len(briefs)} concept briefs ready")
    print(f"{'=' * 60}\n")

    return {"research_summary": briefs}
