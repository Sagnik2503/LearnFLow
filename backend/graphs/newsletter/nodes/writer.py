from langchain_groq import ChatGroq
from schema.schemas import ContentState, SyllabusItem
from prompts.prompt import WRITER_PROMPT
import os


def writer_node(state: ContentState) -> dict:
    print(f"\n{'=' * 60}")
    print("✍️  WRITER NODE")
    print(f"{'=' * 60}")

    plan = state["plan"]
    item = SyllabusItem(**state["item"])

    sections_text = ""
    for section in plan.sections:
        sections_text += f"""
---
Heading: {section.heading}
Concept: {section.concept}
Target Word Count: {section.target_words} words
Key Points to expand on:
{chr(10).join(f"  - {point}" for point in section.key_points)}
---
"""

    research_text = ""
    for brief in state["research_summary"]:
        all_urls = [brief.best_url] + list(brief.additional_urls)
        numbered_urls = "\n".join(f"  [{i}] {url}" for i, url in enumerate(all_urls, 1))
        research_text += f"""
╔══ RESEARCH DOSSIER: {brief.concept} ══╗

Source Article  : {brief.source_title}

[MANDATORY — USE KEY STATISTIC, nearly verbatim]
KEY STATISTIC   : {brief.key_statistic}

[MANDATORY — WEAVE IN, do not replace with generic equivalent]
DIRECT QUOTE    : "{brief.direct_quote}"

[MANDATORY — USE AS PEDAGOGICAL DEPTH in the "how it works" paragraph]
HOW IT WORKS    : {brief.pedagogical_detail}

[Anchor for your core explanation — expand with "why it works this way"]
DEFINITION      : {brief.definition}

[Expand into a blockquote with specific names/numbers/dates]
REAL EXAMPLE    : {brief.example}

[Expand with "why this is surprising" context]
FUN FACT        : {brief.fun_fact}

[NUMBERED URLs — reference these as [1], [2], [3] inline citations in your text]
SOURCES         :
{numbered_urls}

╚═══════════════════════════════════════╝
"""

    prompt = WRITER_PROMPT.format(
        day_number=state["day_number"],
        total_days=state["total_days"],
        newsletter_title=plan.newsletter_title,
        topic_label=item.title,
        hook=plan.hook,
        takeaway=plan.takeaway,
        sections=sections_text,
        research_summaries=research_text,
    )

    # ── Groq Llama ─────────────────
    writer_llm = ChatGroq(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    draft = writer_llm.invoke(prompt).content

    word_count = len(draft.split())

    print(f"   ✅ Draft written — {word_count} words")
    print(f"{'=' * 60}\n")

    return {"draft": draft}
