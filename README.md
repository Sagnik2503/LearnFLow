# 📬 LearnFlow - Daily Learning Newsletter Generator

A LangGraph-powered application that generates a rich, beginner-friendly daily learning newsletter on any topic. Subscribe with your email and receive a personalized syllabus and daily newsletters delivered straight to your inbox.

---

## 🏗️ Architecture

The system consists of three main components:

| Component | Tech | Description |
|-----------|------|-------------|
| **Frontend** | Vanilla JS, HTML, CSS | User interface for subscribing and managing learning tracks |
| **Backend** | FastAPI, Python | REST API handling subscriptions and newsletter generation |
| **Graph Engine** | LangGraph | Orchestrates syllabus and newsletter generation with AI |

---

## 🧠 How It Works

### 1. Subscribe to a Topic
Enter any topic you want to learn (e.g., "Machine Learning", "Photography", "Philosophy").

### 2. AI Generates Your Syllabus
The system creates a personalized multi-day curriculum covering the fundamentals.

### 3. Daily Newsletters
Each day, receive a carefully crafted newsletter that:
- Researches the topic using semantic search (Exa)
- Plans content with a structured brief
- Writes engaging, beginner-friendly prose
- Gets critiqued for clarity and depth
- Formats into clean markdown

---

## 🗂️ Project Structure

```
LearnFlow/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── db/
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── models.py        # ORM models
│   │   └── crud.py          # Database operations
│   ├── schema/
│   │   └── schemas.py       # Pydantic models & TypedDict states
│   ├── graphs/
│   │   ├── builder/         # Graph entry points
│   │   ├── curriculum/      # Syllabus generation graph
│   │   └── newsletter/      # Newsletter generation graph
│   ├── utils/               # Helper utilities
│   ├── prompts/             # LLM prompt templates
│   └── test/                # Manual test scripts
├── frontend/
│   ├── app.js               # Main JavaScript application
│   ├── index.html           # Main HTML
│   ├── index.css            # Styles
│   └── config.js            # Configuration
├── AGENTS.md                # Developer guidelines & code style
├── opencode.json            # OpenCode AI assistant config
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```bash
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key
EXA_API_KEY=your_key
FRONTEND_URL=http://localhost:3000
```

### 3. Run the Backend

```bash
cd backend
uvicorn main:app --reload
```

### 4. Run the Frontend

```bash
python3 -m http.server 3000 --directory frontend
```

Open http://localhost:3000 in your browser.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | REST API framework |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Graph orchestration for newsletter generation |
| [LangChain Anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/) | Planner, Writer, Critic LLM calls |
| [Groq](https://groq.com/) | Fast inference for summarization |
| [Exa](https://exa.ai/) | Semantic search for research |
| [SQLAlchemy](https://www.sqlalchemy.org/) | Database ORM |
| [Pydantic](https://docs.pydantic.dev/) | Data validation |

---


## 🧪 Testing

```bash
# Run a specific test script
cd backend
python test/test_email.py

# Run the test API server
uvicorn test.test_backend:test_app --reload

# Type check
mypy backend/

# Lint
ruff check .

# Format
ruff format .
```

---

## 📋 Design Decisions

**Why Exa over Tavily?**
Exa supports `summary: True` which returns a full AI-generated page summary — far richer than raw snippets.

**Why separate Summarizer from Researcher?**
Raw Exa results exceed model context limits. The Summarizer distills each concept into a `ConceptBrief` (~100 words).

**Why LLM-first writing?**
The LLM owns the narrative for consistent tone and depth. Research enriches with facts and links — it never replaces the writing.

---

## 📝 Developer Guidelines

See [AGENTS.md](./AGENTS.md) for detailed code style, patterns, and conventions.
