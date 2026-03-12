from pydantic import BaseModel, Field
from typing import List, TypedDict


class SyllabusItem(BaseModel):
    day: int = Field(description="Day number in the syllabus")
    title: str = Field(description="Title for the day")
    concepts: List[str] = Field(description="2 to 4 concepts introduced on this day")


class SyllabusOutput(BaseModel):
    syllabus: List[SyllabusItem]


class AgentState(TypedDict):
    topic: str
    total_days: int
    syllabus: list[SyllabusItem]  # [{day, title, goal, concepts}]
    revision_count: int = 0  # tracks retry loops
    quality_score: float = (0.0,)
    track_id: int


class ConceptBrief(BaseModel):
    concept: str
    definition: str  # 1 sentence — what it is
    example: str  # 1 concrete real world example
    fun_fact: str  # 1 surprising or interesting fact
    best_url: str  # single best link for further reading


class ExaResult(BaseModel):
    url: str
    title: str
    snippet: str
    summary: str


class Section(BaseModel):
    concept: str
    heading: str
    key_points: List[str]
    exa_queries: List[str]  # max 2, Exa fires these
    target_words: int = 500


class Plan(BaseModel):
    newsletter_title: str
    hook: str
    tone: str
    sections: List[Section]
    takeaway: str


class Feedback(BaseModel):
    section: str
    issue: str
    suggestion: str


class CriticOutput(BaseModel):
    feedbacks: List[Feedback]
    approved: bool


class ContentState(TypedDict):
    item: SyllabusItem
    plan: Plan | None = None
    research: List[ExaResult] = []
    research_summary: list[ConceptBrief]
    draft: str = ""
    feedback: str = ""
    revision_count: int = 0
    approved: bool = False
    newsletter: str = ""
    feedbacks = List[Feedback]
    revision_count: int = Field(ge=0, le=3)
