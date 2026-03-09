# 📬 Daily Learning Newsletter Generator

A LangGraph-powered application that generates a rich, beginner-friendly daily learning newsletter on any topic. Given a syllabus item for the day, it researches, plans, writes, critiques, and formats a polished markdown newsletter — automatically.

---

## 🧠 How It Works

The system is split into two graphs:

### Graph 1 — Syllabus Generator
Takes a topic and generates a structured multi-day syllabus.

```
Input: topic, total_days
parse_input → generate_syllabus → save to DB
Output: list of { day, title, concepts }
```

### Graph 2 — Daily Content Generator
Takes one syllabus item and produces a full newsletter.

```
Planner → Researcher → Summarizer → Writer → Critic → Formatter
Output: formatted markdown newsletter
```

---

## 🔁 Graph 2 — Node Breakdown

| Node | Input | Output | Description |
|---|---|---|---|
| **Planner** | `item` | `plan` | LLM builds a writing brief — title, hook, sections, tone |
| **Researcher** | `plan.exa_queries` | `research` | Fires targeted Exa searches per concept |
| **Summarizer** | `research` | `research_summary` | Distills raw results into one `ConceptBrief` per concept |
| **Writer** | `plan + research_summary` | `draft` | LLM writes the full newsletter, weaving in research |
| **Critic** | `draft` | `feedback, approved` | Reviews for depth, clarity, and beginner-friendliness |
| **Formatter** | `draft` | `newsletter` | Final clean markdown output |

### Critic Loop
- Critic annotates flagged sections with specific issues and suggestions
- Writer patches **only** the flagged sections (not a full rewrite)
- Auto-approves after **2 revision cycles**

---

## 🗂️ Project Structure

```
├── graphs/
│   ├── syllabus_graph.py        # Graph 1
│   └── content_graph.py         # Graph 2
├── nodes/
│   ├── planner_node.py
│   ├── researcher_node.py
│   ├── summarizer_node.py
│   ├── writer_node.py
│   ├── critic_node.py
│   └── formatter_node.py
├── schemas/
│   └── content_state.py         # All Pydantic models + TypedDict state
├── outputs/                     # Generated newsletters saved here
└── README.md
```

---

## 📐 Schemas

```python
# Input
class SyllabusItem(BaseModel):
    day: int
    title: str
    concepts: List[str]

# Research
class ExaResult(BaseModel):
    url: str
    title: str
    summary: str
    snippet: str

# Planner output
class Section(BaseModel):
    concept: str
    heading: str
    key_points: List[str]
    exa_queries: List[str]      # max 2 per concept
    target_words: int = 400

class Plan(BaseModel):
    newsletter_title: str
    hook: str
    audience: str
    tone: str
    sections: List[Section]
    takeaway: str

# Summarizer output
class ConceptBrief(BaseModel):
    concept: str
    definition: str             # 1 crisp sentence
    example: str                # 1 concrete real world example
    fun_fact: str               # 1 surprising fact
    best_url: str               # best link for further reading

# Graph 2 state
class ContentState(TypedDict):
    item: dict
    plan: Plan | None
    research: list[ExaResult]
    research_summary: list[ConceptBrief]
    draft: str
    feedback: str
    revision_count: int
    approved: bool
    newsletter: str
```

---

## 🚀 Usage

```python
from graphs.content_graph import graph

result = graph.invoke({
    "item": {
        "day": 1,
        "title": "What You Eat Is What You Are",
        "concepts": ["Macronutrients", "Micronutrients", "Gut Health"]
    },
    "plan": None,
    "research": [],
    "research_summary": [],
    "draft": "",
    "feedback": "",
    "revision_count": 0,
    "approved": False,
    "newsletter": ""
})

print(result["newsletter"])
```

---

## 🛠️ Stack

| Tool | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Graph orchestration |
| [LangChain Anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/) | Planner, Writer, Critic nodes |
| [Groq](https://groq.com/) | Summarizer node (fast inference) |
| [Exa](https://exa.ai/) | Semantic search for research |
| Pydantic | Structured LLM outputs |

---

## ⚙️ Environment Variables

```bash
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key
EXA_API_KEY=your_key
```

---

## 📋 Design Decisions

**Why Exa over Tavily?**
Exa supports `summary: True` which returns a full AI-generated page summary — far richer than raw snippets. Combined with `highlights`, it gives the Writer both depth and specific facts.

**Why separate Summarizer from Researcher?**
Raw Exa results (30 results × full summaries) exceed model context limits. The Summarizer distills each concept down to a `ConceptBrief` (~100 words) — keeping the Writer prompt tight and focused.

**Why LLM-first writing?**
The LLM owns the narrative for consistent tone and depth. Research enriches with real facts, examples, and links — it never replaces the writing. This avoids stitched-together, inconsistent content.
