# Agent Instructions for LearnFlow

## Project Overview

LearnFlow is a LangGraph-powered daily learning newsletter generator. It has two main components:

- **Backend**: Python 3.13, FastAPI, LangGraph, SQLAlchemy, Pydantic
- **Frontend**: Vanilla JavaScript, HTML, CSS

## Repository Structure

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
└── frontend/
    ├── app.js               # Main JavaScript application
    ├── index.html           # Main HTML
    ├── index.css            # Styles
    └── config.js            # Configuration
```

---

## Build / Run / Test Commands

### Backend (Python)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Run the API server
uvicorn main:app --reload

# Run with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run a single test script directly
python test/test_email.py

# Run test backend server (separate FastAPI instance)
uvicorn test.test_backend:test_app --reload

# Run pytest (if installed)
pytest

# Run a specific test
pytest test/test_backend.py -v

# Type check with mypy
mypy backend/

# Format code
ruff format .

# Lint code
ruff check .
```

### Frontend (Static Files)

```bash
# Serve frontend files
python3 -m http.server 3000 --directory frontend

# Or for test page:
python3 -m http.server 3000 --directory backend/test
# Then open: http://localhost:3000/test_frontend_index.html
```

### Environment Variables

Create `backend/.env` from `.env.example`:

```bash
cp .env.example .env
```

Required variables:
- `ANTHROPIC_API_KEY` - Anthropic/Claude API key
- `GROQ_API_KEY` - Groq API key
- `EXA_API_KEY` - Exa search API key
- `FRONTEND_URL` - Frontend URL for CORS (optional, defaults to "*")

---

## Code Style Guidelines

### Python

#### Formatting
- 4 spaces for indentation (no tabs)
- Single blank line between top-level definitions
- No blank line at end of file
- Max line length: 100 characters (soft)
- Use `uv ruff format` for automatic formatting

#### Imports
- Standard library imports first
- Third-party imports second
- Local application imports third
- Separate groups with blank lines
- Use absolute imports when possible
- Sort imports alphabetically within groups

```python
# Correct order:
import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from db.models import User
from schema.schemas import SubscribeRequest
```

#### Type Annotations
- Use type hints for all function parameters and return values
- Use `TypedDict` for graph state (see `schema/schemas.py`)
- Use `Pydantic` for API request/response models

```python
# Function with type hints
def get_track(db: Session, track_id: int) -> Track | None:
    ...

# TypedDict for graph state
class ContentState(TypedDict):
    item: SyllabusItem
    plan: Plan | None
    research: list[ExaResult]
```

#### Pydantic Models
- Use `Field()` with descriptions for all fields
- Use `BaseModel` for API models
- Use `TypedDict` for LangGraph state

```python
class SubscribeRequest(BaseModel):
    topic: str = Field(description="Topic to learn")
    email: str = Field(description="Email for daily newsletters")
    delivery_time: str = Field(default="09:00", description="Time to receive newsletter (HH:MM)")
```

#### Naming Conventions
- `PascalCase` for classes: `class SubscribeRequest`
- `snake_case` for functions/variables: `def get_or_create_user`
- `SCREAMING_SNAKE_CASE` for constants: `MAX_RETRIES = 3`
- `_snake_case` for private methods: `def _validate_input`
- Use descriptive names (avoid single letters except in short loops)

#### Error Handling
- Use `try/finally` for database sessions to ensure cleanup
- Raise `HTTPException` for API errors (FastAPI)
- Print error messages with emoji for visibility: `print(f"❌ Error: {e}")`
- Let exceptions propagate for unexpected errors

```python
# Database session pattern
db = SessionLocal()
try:
    user = get_or_create_user(db, email)
    return user
finally:
    db.close()

# API error handling
if not track:
    raise HTTPException(status_code=404, detail="Track not found")
```

#### SQLAlchemy Patterns
- Use `session.query(Model)` syntax (not `select()`)
- Always use `.filter()` or `.filter_by()` with explicit conditions
- Use `relationship()` for foreign key connections
- Set `cascade="all, delete-orphan"` for dependent relationships

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    
    tracks = relationship("UserTrack", back_populates="user", cascade="all, delete-orphan")
```

#### LangGraph Patterns
- Each node is a separate function in `nodes/` directory
- Nodes receive state and return state updates (not full state)
- Use TypedDict for state definition
- Build graph in `graph.py`, export compiled graph

```python
# Node function signature
def parse_input(state: AgentState) -> AgentState:
    # Return only the fields to update
    return {"topic": state["topic"].strip()}

# Graph building
def build_curriculum_graph():
    g = StateGraph(AgentState)
    g.add_node("parse_input", parse_input)
    # ...
    return g.compile()
```

### JavaScript (Frontend)

#### Formatting
- 2 spaces for indentation
- Semicolons required
- Use `const` and `let` (no `var`)
- Use template literals for string interpolation

#### Naming
- `camelCase` for variables and functions: `const deliveryTime`
- `PascalCase` for constructors/classes: not used in this project
- ALL_CAPS for constants: `const API_BASE`

#### Async/Await
- Always use `async/await` for API calls
- Handle errors with try/catch
- Use `console.error` for error logging

```javascript
async function handleSubmit(e) {
  e.preventDefault();
  try {
    const res = await fetch(`${API_BASE}/api/generate-syllabus`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, email }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }
    const data = await res.json();
    return data;
  } catch (err) {
    console.error('Submit failed:', err);
    showToast(err.message, 'error');
  }
}
```

---

## Testing Guidelines

### Running Tests
- Manual test scripts in `backend/test/`
- Run individual scripts directly: `python test/test_email.py`
- Test backend server: `uvicorn test.test_backend:test_app --reload`

### Writing Tests
- Test file naming: `test_<module_name>.py`
- Initialize database and dependencies at module level when needed
- Use `if __name__ == "__main__"` block for execution

```python
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal, init_db
from dotenv import load_dotenv

load_dotenv()
init_db()

def run_test():
    # Test code here
    pass

if __name__ == "__main__":
    run_test()
```

---

## Database Conventions

- SQLite for local development (`learnflow.db`)
- Use `SessionLocal()` for database sessions
- Always close sessions in `finally` block
- Use `db.commit()` after `db.add()` for writes
- Use `db.refresh()` after commits to get generated IDs

---

## API Design Principles

- RESTful endpoints under `/api/` prefix
- Return Pydantic models as response models
- Use appropriate HTTP status codes (200, 400, 404, 500)
- Always validate input and return clear error messages
- Use async/await for all route handlers

---

## Common Patterns

### Adding a new API endpoint

```python
@app.get("/api/resource/{id}", response_model=ResourceResponse)
async def get_resource(id: int):
    db = SessionLocal()
    try:
        resource = get_resource_by_id(db, id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource
    finally:
        db.close()
```

### Adding a new database model

```python
class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NewModel id={self.id} name={self.name!r}>"
```

### Adding a new LangGraph node

```python
# In graphs/module/nodes/new_node.py
def new_node(state: ModuleState) -> ModuleState:
    # Process state
    result = process(state["input"])
    # Return state updates
    return {"output": result, "status": "completed"}
```
