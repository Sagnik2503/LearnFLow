from pydantic import BaseModel, Field
from typing import List, TypedDict


class SyllabusItem(BaseModel):
    day: int = Field(description="Day number in the syllabus")
    title: str = Field(description="Title for the day")
    concepts: List[str] = Field(description="2 to 4 concepts introduced on this day")


class Source(BaseModel):
    url: str = Field(description="URL of the source")
    title: str = Field(description="Title of the article")
    content: str = Field(description="Relevant extracted content from the page")
    quality_score: float = Field(
        description="Quality score between 0 and 10", ge=0, le=10
    )


class FilteredSources(BaseModel):
    filtered_sources: List[Source] = Field(
        description="Top 5 best sources for learning the topic"
    )


class SyllabusOutput(BaseModel):
    syllabus: List[SyllabusItem]


class AgentState(TypedDict):
    topic: str
    total_days: int
    syllabus: list[SyllabusItem]  # [{day, title, goal, concepts}]
    revision_count: int = 0  # tracks retry loops
    quality_score: float = (0.0,)
    track_id: int
