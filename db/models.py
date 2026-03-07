from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False)
    total_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    syllabus_items = relationship(
        "SyllabusItem", back_populates="track", cascade="all, delete-orphan"
    )
    day_cards = relationship(
        "DayCard", back_populates="track", cascade="all, delete-orphan"
    )


class SyllabusItem(Base):
    __tablename__ = "syllabus_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    day = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    concepts = Column(JSON, nullable=False)  # stored as a JSON array

    track = relationship("Track", back_populates="syllabus_items")

    def __repr__(self):
        return (
            f"<SyllabusItem track={self.track_id} day={self.day} title={self.title!r}>"
        )


class DayCard(Base):
    __tablename__ = "day_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    day = Column(Integer, nullable=False)
    hook = Column(String, nullable=False)
    body = Column(String, nullable=False)
    takeaways = Column(JSON, nullable=False)  # list[str]
    diagram_code = Column(String, nullable=True)  # Mermaid string
    diagram_type = Column(String, nullable=True)  # "mindmap" | "flowchart" etc
    sources = Column(JSON, nullable=True)  # [{title, url, summary}]
    created_at = Column(DateTime, default=datetime.utcnow)

    track = relationship("Track", back_populates="day_cards")

    def __repr__(self):
        return f"<DayCard track={self.track_id} day={self.day}>"
