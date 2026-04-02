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


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tracks = relationship(
        "UserTrack", back_populates="user", cascade="all, delete-orphan"
    )


class UserTrack(Base):
    __tablename__ = "user_tracks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    current_day = Column(Integer, default=1)
    total_days = Column(Integer, nullable=False)
    delivery_time = Column(String, nullable=False, default="09:00")
    active = Column(Integer, default=1)
    last_seen = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tracks")
    track = relationship("Track")
    newsletters = relationship(
        "GeneratedNewsletter", back_populates="user_track", cascade="all, delete-orphan"
    )


class GeneratedNewsletter(Base):
    __tablename__ = "generated_newsletters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_track_id = Column(Integer, ForeignKey("user_tracks.id"), nullable=False)
    day = Column(Integer, nullable=False)

    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_track = relationship("UserTrack", back_populates="newsletters")
