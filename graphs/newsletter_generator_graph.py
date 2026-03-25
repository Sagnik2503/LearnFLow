from schema.schemas import (
    ContentState,
    ExaResult,
    ConceptBrief,
    Plan,
    CriticOutput,
    SyllabusItem,
)
from langgraph.graph import StateGraph, START, END

from langchain_groq import ChatGroq
import os
from exa_py import Exa
from dotenv import load_dotenv
from prompts.prompt import (
    PLANNER_PROMPT,
    WRITER_PROMPT,
    CRITIC_PROMPT,
    SUMMARIZER_PROMPT,
)

load_dotenv()


exa = Exa(api_key=os.getenv("EXA_API_KEY"))
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


def planner_node(state: ContentState) -> dict:

    prompt = PLANNER_PROMPT.format(
        day=state["item"]["day"],
        title=state["item"]["title"],
        concepts=", ".join(state["item"]["concepts"]),
    )
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY")
    )
    plan = llm.with_structured_output(Plan).invoke(prompt)

    return {"plan": plan}


def research_node(state: ContentState) -> dict:
    """Based on the exa queries defined in the planner node, the exa search will be triggered"""

    exa_queries_list = []
    for section in state["plan"].sections:
        for query in section.exa_queries:
            exa_queries_list.append(query)

    print(f"\n{'='*60}")
    print(f"🔍 RESEARCHER NODE")
    print(f"{'='*60}")
    print(f"📋 Total queries to run: {len(exa_queries_list)}")
    for i, q in enumerate(exa_queries_list, 1):
        print(f"   {i}. {q}")

    query_results = []
    seen_urls = set()
    for query in exa_queries_list:
        print(f"\n🔎 Searching: '{query}'")
        result = exa.search(
            query,
            type="auto",
            num_results=2,
            contents={
                "highlights": {"max_characters": 4000},
                "text": True,
                "summary": True,
            },
            include_domains=[
                "developers.google.com",
                "coursera.org",
                "arxiv.org",
                "datacamp.com",
                "baeldung.com",
                "wikipedia.org",
                "towardsdatascience.com",
            ],
        )
        for item in result.results:
            if item.url in seen_urls:
                continue

            seen_urls.add(item.url)
            exa_result = ExaResult(
                url=item.url,
                title=item.title,
                summary=item.summary if item.summary else "",
                snippet=item.highlights[0] if item.highlights else "",
            )
            query_results.append(exa_result)
            print(f"   ✅ {item.title}")
            print(f"      🔗 {item.url}")
            print(f"      📝 {exa_result.snippet[:100]}...")

    print(f"\n{'='*60}")
    print(f"✅ Research complete — {len(query_results)} results collected")
    print(f"{'='*60}\n")

    return {"research": query_results}


def research_node(state: ContentState) -> dict:
    """Based on the exa queries defined in the planner node, the exa search will be triggered"""

    exa_queries_list = []
    for section in state["plan"].sections:
        for query in section.exa_queries:
            exa_queries_list.append(query)

    print(f"\n{'='*60}")
    print(f"🔍 RESEARCHER NODE")
    print(f"{'='*60}")
    print(f"📋 Total queries to run: {len(exa_queries_list)}")
    for i, q in enumerate(exa_queries_list, 1):
        print(f"   {i}. {q}")

    query_results = []
    seen_urls = set()
    for query in exa_queries_list:
        print(f"\n🔎 Searching: '{query}'")
        result = exa.search(
            query,
            type="auto",
            num_results=2,
            contents={
                "highlights": {"max_characters": 4000},
                "text": True,
                "summary": True,
            },
            include_domains=[
                "developers.google.com",
                "coursera.org",
                "arxiv.org",
                "datacamp.com",
                "baeldung.com",
                "wikipedia.org",
                "towardsdatascience.com",
            ],
        )
        for item in result.results:
            if item.url in seen_urls:
                continue

            seen_urls.add(item.url)
            exa_result = ExaResult(
                url=item.url,
                title=item.title,
                summary=item.summary if item.summary else "",
                snippet=item.highlights[0] if item.highlights else "",
            )
            query_results.append(exa_result)
            print(f"   ✅ {item.title}")
            print(f"      🔗 {item.url}")
            print(f"      📝 {exa_result.snippet[:100]}...")

    print(f"\n{'='*60}")
    print(f"✅ Research complete — {len(query_results)} results collected")
    print(f"{'='*60}\n")

    return {"research": query_results}


def summarizer_node(state: ContentState) -> dict:

    print(f"\n{'='*60}")
    print("📝 SUMMARIZER NODE")
    print(f"{'='*60}")

    plan = state["plan"]
    research = state["research"]

    print(f"📋 Total raw results: {len(research)}")

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

    # group results by concept using exa_queries order
    results_per_concept = len(research) // len(plan.sections)

    briefs = []
    for i, section in enumerate(plan.sections):
        start = i * results_per_concept
        end = start + results_per_concept
        concept_results = research[start:end]

        print(f"\n🔎 Distilling: '{section.concept}' ({len(concept_results)} results)")

        # format only what matters — trim aggressively
        raw_results = "\n\n".join(
            [
                f"Title: {r.title}\nURL: {r.url}\nSummary: {r.summary[:300]}\nSnippet: {r.snippet[:150]}"
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


def writer_node(state: ContentState) -> dict:

    print(f"\n{'='*60}")
    print(f"✍️  WRITER NODE")
    print(f"{'='*60}")

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
{chr(10).join(f'  - {point}' for point in section.key_points)}
---
"""

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
    writer_llm = ChatGroq(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=os.getenv("GROQ_API"),
    )
    draft = writer_llm.invoke(prompt).content
    word_count = len(draft.split())

    print(f"   ✅ Draft written — {word_count} words")
    print(f"{'='*60}\n")

    return {"draft": draft}


def critic_node(state: ContentState) -> ContentState:
    """this node will give feedback based on the content that has been generated for the newsletter"""

    print(f"\n{'='*60}")
    print(f"🔍 CRITIC NODE")
    print(f"{'='*60}")

    revision_count = state.get("revision_count", 0)

    # auto approve after 3 cycles
    if revision_count >= 2:
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
    """
    Routes to 'writer' for another pass, or 'end' when done.
    Called after critic_node.
    """
    if state["approved"]:
        return "end"
    if state["revision_count"] >= 2:
        return "end"
    return "writer"


def finalizer_node(state: ContentState) -> dict:
    return {"newsletter": state["draft"]}


def build_graph():
    g = StateGraph(ContentState)

    # Add node
    g.add_node("planner_node", planner_node)
    g.add_node("research_node", research_node)
    g.add_node("writer_node", writer_node)
    g.add_node("critic_node", critic_node)
    g.add_node("finalizer_node", finalizer_node)
    # Connect start → node
    g.add_edge(START, "planner_node")
    g.add_edge("planner_node", "research_node")
    g.add_edge("research_node", "writer_node")
    g.add_edge("writer_node", "critic_node")
    g.add_edge("critic_node", "finalizer_node")
    g.add_conditional_edges(
        "critic_node",  # source node
        should_revise,  # function that returns the next node name
        {
            "writer": "writer_node",  # needs revision → back to writer
            "end": "finalizer_node",  # approved (or max revisions hit) → done
        },
    )
    g.add_edge("finalizer_node", END)
    return g.compile()
