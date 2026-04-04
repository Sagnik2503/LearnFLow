from graphs.builder.curriculum_builder import run_curriculum_graph
from graphs.builder.newsletter_builder import run_newsletter_graph
from db.crud import (
    create_subscription,
    get_newsletter,
    get_previous_title,
    create_newsletter,
    get_user_track,
    get_track,
)
from sqlalchemy.orm import Session
from db.models import SyllabusItem


def start_topic(db: Session, user_id: int, topic: str, delivery_time: str):
    print(f"\n🚀 Starting topic: {topic}")

    result = run_curriculum_graph(topic)
    track_id = result["track_id"]
    total_days = result["total_days"]

    print(f"📘 Generated syllabus with {total_days} days (track {track_id})")

    user_track = create_subscription(db, user_id, track_id, total_days, delivery_time)

    print(f"✅ UserTrack created (Day 1)")

    return user_track


def build_newsletter(db: Session, track_id: int, day: int) -> str:
    """
    Generate newsletter content for a specific day of a track.
    Fetches syllabus item, track info, and previous title automatically.
    """
    track = get_track(db, track_id)
    if not track:
        raise ValueError(f"Track {track_id} not found")

    syllabus_item = db.query(SyllabusItem).filter_by(track_id=track_id, day=day).first()
    if not syllabus_item:
        raise ValueError(f"No syllabus found for day {day} in track {track_id}")

    prev_title = get_previous_title(db, track_id, day)

    content = run_newsletter_graph(
        topic=track.topic,
        item={
            "day": syllabus_item.day,
            "title": syllabus_item.title,
            "description": "",
            "concepts": syllabus_item.concepts,
        },
        day=day,
        total_days=track.total_days,
    )

    return content


def get_today_newsletter(db: Session, user_id: int, track_id: int):
    print(f"\n📬 Fetching newsletter for user={user_id}")

    user_track = get_user_track(db, user_id, track_id)

    if not user_track:
        raise ValueError("UserTrack not found")

    day = user_track.current_day

    newsletter = get_newsletter(db, user_track.id, day)
    if newsletter:
        print("⚡ Using cached newsletter")
        return newsletter.content

    content = build_newsletter(db, track_id, day)
    create_newsletter(db, user_track.id, day, content)

    print("💾 Newsletter saved")

    return content


def generate_and_save_newsletter(db: Session, user_track) -> bool:
    """
    Generate newsletter for the user_track's current_day and save to DB.
    Skips if already generated. Returns True if generated, False if skipped.
    """
    day = user_track.current_day

    existing = get_newsletter(db, user_track.id, day)
    if existing:
        print(f"  ⏭️  Day {day} already generated for user_track {user_track.id}")
        return False

    content = build_newsletter(db, user_track.track_id, day)
    create_newsletter(db, user_track.id, day, content)

    print(f"  ✅ Day {day} newsletter generated for user_track {user_track.id}")
    return True

