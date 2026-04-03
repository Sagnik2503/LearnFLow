from sqlalchemy.orm import Session
from db.models import Track, SyllabusItem, User, UserTrack, GeneratedNewsletter


def create_user(db: Session, email: str):
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_subscription(db: Session, user_id: int, track_id: int, total_days: int, delivery_time: str):
    user_track = UserTrack(
        user_id=user_id,
        track_id=track_id,
        current_day=1,
        total_days=total_days,
        delivery_time=delivery_time,
    )
    db.add(user_track)
    db.commit()
    db.refresh(user_track)
    return user_track


def get_active_subscriptions(db: Session):
    return (
        db.query(UserTrack)
        .filter(UserTrack.active == 1, UserTrack.current_day <= UserTrack.total_days)
        .all()
    )

def get_newsletter(db: Session, user_track_id: int, day: int):
    return (
        db.query(GeneratedNewsletter)
        .filter_by(user_track_id=user_track_id, day=day)
        .first()
    )

def get_user_track(db: Session, user_id: int, track_id: int):
    return db.query(UserTrack).filter_by(user_id=user_id, track_id=track_id).first()

def create_newsletter(db: Session, user_track_id: int, day: int, content: str):
    newsletter = GeneratedNewsletter(
        user_track_id=user_track_id,
        day=day,
        content=content,
    )
    db.add(newsletter)
    db.commit()
    db.refresh(newsletter)
    return newsletter

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


def unsubscribe(db: Session, user_track_id: int):
    user_track = db.query(UserTrack).filter(UserTrack.id == user_track_id).first()
    if user_track:
        user_track.active = 0
        db.commit()
        db.refresh(user_track)
    return user_track
