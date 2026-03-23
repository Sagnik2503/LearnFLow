from pydantic import BaseModel, Field
from typing import List, TypedDict


class SyllabusItem(BaseModel):
    day: int = Field(description="Day number in the syllabus")
    title: str = Field(description="Title for the day")
    description: str = Field(  # ← NEW
        description=(
            "2–3 sentence teaser shown to the reader before they open the day's newsletter. "
            "Written in second-person ('You'll discover…', 'By the end of today…'). "
            "Specific and curious — not generic like 'We cover the basics.'"
        )
    )
    concepts: List[str] = Field(description="2 to 4 concepts introduced on this day")


class AgentState(TypedDict):
    topic: str
    total_days: int
    syllabus: list[SyllabusItem]  # [{day, title, goal, concepts}]
    track_id: int


class SyllabusOutput(BaseModel):
    syllabus: List[SyllabusItem]


class DaysDecision(BaseModel):
    total_days: int = Field(
        ge=3,
        le=14,
        description="Number of days needed to cover this topic well for a beginner",
    )


from typing import List
from pydantic import BaseModel


class SyllabusItem(BaseModel):
    day: int
    title: str
    description: str
    concepts: List[str]


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
    key_points: List[str] = Field(description="Exactly 3 key points, no more")
    exa_queries: List[str] = Field(description="Exactly 2 search queries, no more")
    target_words: int = Field(default=500, description="Always 500")


class Plan(BaseModel):
    newsletter_title: str
    hook: str
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
    day_number: int
    total_days: int
    plan: Plan | None
    research: List[ExaResult]
    research_summary: List[ConceptBrief]
    draft: str
    feedback: str
    feedbacks: List[Feedback]
    revision_count: int
    approved: bool
    newsletter: str
