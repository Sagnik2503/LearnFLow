from schemas.schemas import (
    ContentState,
    ExaResult,
    ConceptBrief,
    Plan,
    Feedback,
    CriticOutput,
)
from langchain_groq import ChatGroq
import os
from langgraph.graph import START, END, StateGraph
from exa_py import Exa
from dotenv import load_dotenv

load_dotenv()


exa = Exa(api_key=os.getenv("EXA_API_KEY"))
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


def planner_node(state: ContentState) -> dict:
    PLANNER_PROMPT = """
You are creating the outline for a modern tech newsletter lesson.

The writing style should feel like popular tech newsletters such as TLDR, The Neuron, or AI Brew: smart, conversational, and easy to skim.

The reader should feel like they learned something useful in under 60 seconds.

Your job is NOT to write the full article. Your job is to produce a structured PLAN that a writer will expand into the final newsletter section.

--------------------------------------------------

INPUTS

Day: {day}
Topic Title: {title}
Concepts: {concepts}

--------------------------------------------------

TASK

Create a structured plan for a newsletter lesson.

--------------------------------------------------

INSTRUCTIONS

1. NEWSLETTER TITLE

Write a catchy newsletter-style title.

The title should:
- spark curiosity
- feel modern
- avoid textbook wording

Examples:
"Neural Networks: The Brains Behind Modern AI"
"The 3 Building Blocks Powering Every AI System"

--------------------------------------------------

2. HOOK (2–3 sentences)

Write a short opening hook that grabs attention.

The hook should:
- introduce the topic quickly
- create curiosity
- explain why the reader should care

Example tone:

"Every AI system you hear about — from ChatGPT to self-driving cars — runs on the same core idea: neural networks.

But the strange part? These powerful systems are built from extremely simple mathematical units.

Today we'll break down the three building blocks that make it all work."

--------------------------------------------------

3. SECTIONS

For EACH concept create a section containing:

heading  
An engaging section title.

Avoid generic titles like:
"Introduction to..."

Examples:
"Meet the Tiny Neurons Running the Show"
"Stacking Layers to Build Intelligence"

key_points

Write 3–5 bullet ideas explaining HOW the concept works.

Rules:
- explain the mechanism
- avoid vague statements
- focus on intuition
- keep sentences short

Bad example:
"Neurons process data"

Good example:
"A neuron takes numbers as input and multiplies them by learned weights."

exa_queries

Provide up to 2 search queries that would help find:
- examples
- case studies
- explanations
NOTE - that since exa is scemantic, the queries should be best designed for learning purposes.

Queries should be specific and useful.

--------------------------------------------------

4. STYLE GUIDELINES

The final article should feel:

• clear  
• engaging  
• beginner friendly  
• easy to skim  

Use:
- short sentences
- concrete explanations
- intuitive mental models

Avoid:
- academic language
- textbook definitions
- vague bullet points

--------------------------------------------------

5. TAKEAWAY

End with one memorable sentence capturing the big idea.

Example:

"Big idea: neural networks turn simple math operations into powerful pattern-recognition machines."

--------------------------------------------------

OUTPUT REQUIREMENTS

Return ONLY valid JSON matching the Plan schema.

Important rules:

- "sections" MUST be a JSON array
- Do NOT wrap arrays or objects as strings
- Do NOT include markdown
- Do NOT include explanations
- Do NOT include text outside the JSON

...
Return a valid Plan object with these exact fields:
- newsletter_title (not 'name', not 'title')
- hook
- tone
- sections
- takeaway
...
"""

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


def summarizer_node(state: ContentState) -> dict:
    SUMMARIZER_PROMPT = """
        You are a research distiller for a beginner-friendly learning newsletter.

        You will be given raw research results for a specific concept.
        Your job is to extract only the most valuable pieces for a newsletter writer.

        Concept: {concept}

        Raw Research:
        {raw_results}

        Extract exactly:
        - definition: one crisp sentence explaining what this concept is
        - example: one concrete real world example that makes it click for a beginner
        - fun_fact: one surprising or interesting fact that will make the reader go "wow"
        - best_url: the single most beginner friendly and informative URL from the results

        Be specific. No vague generalities.
        Return a valid ConceptBrief object."""
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

    WRITER_PROMPT = """
    You are a newsletter writer writing a daily learning newsletter.

    Your job is to write a fun, engaging, beginner-friendly newsletter in markdown.

    ---

    Newsletter Plan:
    - Title: {newsletter_title}
    - Hook: {hook}
    - Audience: Cater to a range of audience from beginner to intermediate
    - Tone: the tone should be engaging while being formal and informative
    - Takeaway: {takeaway}

    Sections:
    {sections}

    Research (weave naturally into your writing):
    {research_summaries}

    ---

    Writing Rules:

    1. Start with the hook as a punchy opening — 3-4 sentences that grab attention

    2. For each section write in this exact order:

    a) INTRO (2-3 sentences): Frame the concept — what is it and why should the reader care
    
    b) WHAT (4-5 sentences): Explain clearly what this concept is using your own knowledge
        - Use **bold** when introducing a key term for the first time
        - Keep sentences short and direct
    
    c) HOW (5-6 sentences): Go deeper — explain the mechanics step by step
        - Explain WHY it works this way
        - Use a simple analogy if it helps
    
    d) 💡 **Fun fact:** (2-3 sentences): Use the fun fact from research — make it surprising
    
    e) EXAMPLE (4-5 sentences): 
        > **For example:** Concrete real world example from research with specific details
    
    f) WHY IT MATTERS (3-4 sentences): Tell the reader why this concept is important
        - Connect it to something they already know or care about
    
    g) 📖 **Dive deeper:** [best URL from research]

    3. End with the takeaway as a 3-4 sentence closing paragraph

    ---

    Formatting Rules:
    - Each paragraph: 3-5 sentences — never more, never less
    - Blank line between EVERY paragraph and element
    - NO walls of text
    - NO subheadings within sections
    - Use emojis sparingly — max 2 per section
    - Use bullet points ONLY when listing 3+ distinct items

    ---

    Word Count Rules (NON-NEGOTIABLE):
    - Each section MUST be at least 350 words
    - Total newsletter MUST be at least 1200 words
    - After writing, count the words in each section
    - If any section is under 350 words, expand the HOW and EXAMPLE parts

    ---

    GOOD example of a section:

    ## Meet the Tiny Neurons Running the Show

    Neurons are the fundamental units of a neural network — and they're surprisingly simple. You don't need a PhD to understand them. By the end of this section, you'll know exactly how they work.

    A **neuron** takes a set of numbers as input and multiplies each one by a learned **weight**. The weighted values are then summed together. This sum is passed through an **activation function** to produce a single output value. That output is then passed on to the next neuron in the network.

    The **weight** is what makes learning possible. Think of it like a volume knob — a high weight means "this input really matters," while a low weight means "mostly ignore this." During training, these weights are adjusted thousands of times based on how wrong the network's predictions are. This process is called **backpropagation**, and it's how neural networks get smarter over time. The network essentially keeps tweaking the knobs until it gets the right answer consistently.

    💡 **Fun fact:** The human brain has 86 billion neurons, each connected to thousands of others. GPT-4 has roughly 1.8 trillion parameters — each one acting like a tiny weighted connection between artificial neurons.

    > **For example:** When a neural network is trained to recognize handwritten digits, each neuron in the first layer looks at a small patch of pixels. One neuron might learn to detect a horizontal edge. Another detects a curve. By combining thousands of these simple detections across multiple layers, the network can confidently tell the difference between a 3 and an 8 — something that seems effortless to humans but requires millions of calculations.

    Understanding neurons matters because they are the reason neural networks can learn anything at all. Without the weight-adjustment mechanism, the network would just be a static math formula. The ability to update weights based on feedback is what separates a learning system from a lookup table. Every AI breakthrough you've heard of — from image recognition to language models — is built on this simple idea.

    📖 **Dive deeper:** https://www.baeldung.com/cs/neural-networks-neurons

    ---

    Return only the final markdown. No preamble, no explanation, just the newsletter.
    """

    print(f"\n{'='*60}")
    print(f"✍️  WRITER NODE")
    print(f"{'='*60}")

    plan = state["plan"]

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
        newsletter_title=plan.newsletter_title,
        hook=plan.hook,
        tone=plan.tone,
        takeaway=plan.takeaway,
        sections=sections_text,
        research_summaries=research_text,
    )

    draft = llm.invoke(prompt).content

    print(f"   ✅ Draft written — {len(draft.split())} words")
    print(f"{'='*60}\n")

    return {"draft": draft}


def build_graph():
    g = StateGraph(ContentState)

    # Add node
    g.add_node("planner_node", planner_node)
    g.add_node("research_node", research_node)
    g.add_node("writer_node", writer_node)

    # Connect start → node
    g.add_edge(START, "planner_node")
    g.add_edge("planner_node", "research_node")
    g.add_edge("research_node", "writer_node")
    g.add_edge("writer_node", END)

    return g.compile()


def critic_node(state: ContentState) -> ContentState:
    """this node will give feedback based on the content that has been generated for the newsletter"""

    CRITIC_PROMPT = """
    You are a strict and senior newsletter editor reviewing a draft for quality.

    Your job is to flag ONLY real problems — do not rewrite, just annotate.

    Draft:
    {draft}

    Review against these rules and flag any violations:

    1. REPETITION
        - Flag any phrase, sentence, or example used more than once across the newsletter
        - Flag any section that ends with the same conclusion as another section

    2. PADDING
        - Flag any sentence that does not teach the reader something specific
        - Flag vague filler phrases like:
        * "you'll gain a deeper appreciation"
        * "every AI breakthrough you've heard of"
        * "by understanding this"
        * "the complexity and beauty of"
        * "something that seems effortless to humans"
        * Any sentence that could be deleted without losing information

    3. SHALLOW EXPLANATION
        - Flag any key point that is stated but never actually explained
        - Flag any claim made without a specific example or fact to back it up

    4. HALLUCINATION RISK
        - Flag any specific number, statistic, or claim that is not grounded in the research provided
        - Do not flag general knowledge claims

    5. REDUNDANT EXAMPLES
        - Flag if the same real world example (e.g. handwritten digits, cat recognition) is used in more than one section
        - Each section MUST use a different example

    ---

    Research used to write this newsletter:
    {research_summaries}

    ---

    For each issue found output:
    - section: which section heading has the problem
    - issue: what exactly is wrong, quote the specific text
    - suggestion: exact instruction to fix it — be specific

    If the newsletter passes all checks set approved = True and annotations = [].

    Return a valid CriticOutput object.
    """
    print(f"\n{'='*60}")
    print(f"🔍 CRITIC NODE")
    print(f"{'='*60}")

    revision_count = state.get("revision_count", 0)

    # auto approve after 3 cycles
    if revision_count >= 3:
        print(f"   ⚠️ Max revisions reached — auto approving")
        return {"approved": True, "feedback": []}

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
    result = llm.with_structured_output(CriticOutput).invoke(prompt)

    print(f"   📋 Annotations: {len(result.feedbacks)}")
    for annotation in result.annotations:
        print(f"   ⚠️  [{annotation.section}] {annotation.issue[:80]}...")
        print(f"   ✅ Approved: {result.approved}")
        print(f"{'='*60}\n")

        return {
            "feedbacks": result.feedbacks,
            "approved": result.approved,
            "revision_count": revision_count + 1,
        }

    if __name__ == "__main__":

        graph = build_graph()
        esult = graph.invoke(
            {
                "item": {
                    "day": 1,
                    "title": "Introduction to Nutritious food",
                    "concepts": ["neurons", "layers", "activation functions"],
                },
                "research_summary": [],
            }
        )
