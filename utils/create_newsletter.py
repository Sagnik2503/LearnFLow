from graphs.builder.curriculum_builder import run_curriculum_graph
from graphs.builder.newsletter_builder import run_newsletter_graph
from graphs.newsletter_generator_graph import build_graph
from db.crud import (
    create_track,
    save_syllabus,
    create_user_track,
    get_newsletter,
    get_previous_title,
    create_newsletter,
    get_user_track,
)
from sqlalchemy.orm import Session
from db.models import SyllabusItem


def start_topic(db: Session, user_id: str, topic: str):
    # 1. Generate syllabus (LLM)
    syllabus = generate_syllabus(topic)

    total_days = len(syllabus)

    # 2. Create trackfrom sqlalchemy.orm import Session


from db.models import SyllabusItem

from graphs.curriculum_graph import generate_syllabus
from graphs.newsletter_generator_graph import build_graph

from db.crud import (
    create_track,
    save_syllabus,
    create_user_track,
    get_newsletter,
    get_previous_title,
    create_newsletter,
    get_user_track,
)

# ✅ Build graph ONCE (important for performance)
newsletter_graph = build_graph()


# -------------------------------
# START TOPIC
# -------------------------------
def start_topic(db: Session, user_id: str, topic: str):
    print(f"\n🚀 Starting topic: {topic}")

    # 1. Generate syllabus
    result = run_curriculum_graph(topic)
    total_days = len(result["syllabus"])

    print(f"📘 Generated syllabus with {total_days} days")

    # 2. Create track
    track = create_track(db, topic, total_days)

    # 3. Save syllabus
    save_syllabus(db, track.id, result["syllabus"])

    # 4. Create user track
    user_track = create_user_track(db, user_id, track.id, total_days)

    print(f"✅ UserTrack created (Day 1)")

    return user_track


# -------------------------------
# GENERATE NEWSLETTER (GRAPH CALL)
# -------------------------------
def generate_newsletter_markdown(
    topic: str,
    concepts: list[str],
    previous: str | None,
    day: int,
    total_days: int,
) -> str:

    graph_input = {
        "topic": topic,
        "concepts": concepts,
        "previous_topic": previous,
        "day": day,
        "total_days": total_days,
    }

    print("\n🧠 Generating newsletter...")
    print("📌 Input:", graph_input)

    try:
        result = run_newsletter_graph.invoke(graph_input)

        # If graph returns dict
        content = result.get("content") if isinstance(result, dict) else result

        if not content:
            raise ValueError("Empty content from graph")

        print("✅ Newsletter generated")

        return content

    except Exception as e:
        print("⚠️ Graph failed, using fallback:", str(e))

        # fallback content
        return f"""
# {topic}

This is Day {day} of your learning journey.

## Concepts Covered
{", ".join(concepts)}

## Summary
- Understand the basics of {topic}
- Learn key ideas step-by-step

## Task
Think about how {topic} applies in real life.
"""


# -------------------------------
# GET TODAY NEWSLETTER
# -------------------------------
from db.crud import get_track  # ⚠️ ADD THIS IMPORT


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
