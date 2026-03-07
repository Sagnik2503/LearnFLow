from sqlalchemy.orm import Session
from db.models import Track, SyllabusItem


def create_track(db: Session, topic: str, total_days: int) -> Track:
    track = Track(topic=topic, total_days=total_days)
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def save_syllabus(
    db: Session, track_id: int, syllabus: list[dict]
) -> list[SyllabusItem]:
    items = []
    for item in syllabus:
        row = SyllabusItem(
            track_id=track_id,
            day=item["day"],
            title=item["title"],
            concepts=item["concepts"],
        )
        db.add(row)
        items.append(row)
    db.commit()
    return items


def get_syllabus(db: Session, track_id: int) -> list[SyllabusItem]:
    return (
        db.query(SyllabusItem)
        .filter(SyllabusItem.track_id == track_id)
        .order_by(SyllabusItem.day)
        .all()
    )


def get_track(db: Session, track_id: int) -> Track | None:
    return db.query(Track).filter(Track.id == track_id).first()


def get_previous_title(db: Session, track_id: int, current_day: int) -> str | None:
    if current_day == 1:
        return None
    item = (
        db.query(SyllabusItem).filter_by(track_id=track_id, day=current_day - 1).first()
    )
    return item.title if item else None
