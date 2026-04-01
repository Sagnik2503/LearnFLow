from graphs.builder.curriculum_builder import run_curriculum_graph
from graphs.builder.newsletter_builder import run_newsletter_graph
from db.crud import (
    create_track,
    save_syllabus,
    create_user_track,
    get_newsletter,
    get_previous_title,
    create_newsletter,
    get_user_track,
    get_track,
)
from sqlalchemy.orm import Session
from db.models import SyllabusItem


# -------------------------------
# START TOPIC
# -------------------------------
def start_topic(db: Session, user_id: str, topic: str):
    print(f"\n🚀 Starting topic: {topic}")

    result = run_curriculum_graph(topic)
    track_id = result["track_id"]
    total_days = result["total_days"]

    print(f"📘 Generated syllabus with {total_days} days (track {track_id})")

    user_track = create_user_track(db, user_id, track_id, total_days)

    print(f"✅ UserTrack created (Day 1)")

    return user_track


def get_today_newsletter(db: Session, user_id: str, track_id: int):
    print(f"\n📬 Fetching newsletter for user={user_id}")

    user_track = get_user_track(db, user_id, track_id)

    if not user_track:
        raise ValueError("UserTrack not found")

    day = user_track.current_day

    # 1. Check cache
    newsletter = get_newsletter(db, user_track.id, day)
    if newsletter:
        print("⚡ Using cached newsletter")
        return newsletter.content

    # 2. Get syllabus
    syllabus_item = db.query(SyllabusItem).filter_by(track_id=track_id, day=day).first()

    if not syllabus_item:
        raise ValueError(f"No syllabus found for day {day}")

    # ⚠️ IMPORTANT: GET TRACK
    track = get_track(db, track_id)

    # 3. Previous topic
    prev_title = get_previous_title(db, track_id, day)

    # 4. Run graph
    content = run_newsletter_graph(
        topic=track.topic,
        item={
            "day": syllabus_item.day,
            "title": syllabus_item.title,
            "description": "",  # optional
            "concepts": syllabus_item.concepts,
        },
        previous=prev_title,
        day=day,
        total_days=user_track.total_days,
    )

    # 5. Save
    create_newsletter(db, user_track.id, day, content)

    print("💾 Newsletter saved")

    return content
