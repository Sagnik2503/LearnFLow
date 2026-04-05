from pydantic import BaseModel, Field, field_validator
from typing import List, TypedDict


class SubscribeRequest(BaseModel):
    topic: str = Field(description="Topic to learn")
    email: str = Field(description="Email for daily newsletters")
    delivery_time: str = Field(
        default="09:00", description="Time to receive newsletter (HH:MM)"
    )


class SubscribeResponse(BaseModel):
    track_id: int
    topic: str
    total_days: int
    message: str


class SyllabusItem(BaseModel):
    day: int = Field(description="Day number in the syllabus")
    title: str = Field(description="Title for the day")
    description: str = Field(
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


class ConceptBrief(BaseModel):
    concept: str
    definition: str  # 1-2 sentences — what it is, in plain language
    example: str  # 1 concrete real-world example — MUST include specific names/numbers
    fun_fact: str  # 1 surprising fact — MUST include a specific number, date, or name
    best_url: str  # single best URL for further reading
    additional_urls: List[str] = Field(
        default_factory=list,
        description="2-3 additional URLs for further reading on this concept",
    )
    # Grounding fields — extracted almost verbatim from source material
    key_statistic: (
        str  # one specific number/date/stat from source, with context sentence
    )
    direct_quote: str  # one short sentence or phrase from the source captured closely
    source_title: str  # title of the primary source article used
    pedagogical_detail: str  # a specific HOW-IT-WORKS mechanism from the source that a beginner wouldn't know without reading it


class ExaResult(BaseModel):
    url: str
    title: str
    snippet: str
    summary: str


class Section(BaseModel):
    concept: str
    heading: str
    key_points: List[str] = Field(description="Exactly 3 key points, no more")
    exa_queries: List[str] = Field(description="Exactly 3 search queries, no more")
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
    approved: str = Field(description="true or false")


class ContentState(TypedDict):
    item: SyllabusItem
    day_number: int
    total_days: int
    plan: Plan | None
    research: List[ExaResult]
    research_summary: List[ConceptBrief]
    draft: str
    feedbacks: List[Feedback]
    revision_count: int
    approved: bool
    newsletter: str
