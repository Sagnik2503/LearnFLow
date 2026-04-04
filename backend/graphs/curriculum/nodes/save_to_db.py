from schema.schemas import AgentState
from db.database import SessionLocal
from db.crud import create_track, save_syllabus


def save_to_db(state: AgentState) -> dict:
    db = SessionLocal()
    try:
        track = create_track(
            db=db,
            topic=state["topic"],
            total_days=state["total_days"],
        )

        save_syllabus(
            db=db,
            track_id=track.id,
            syllabus=state["syllabus"],
        )

        print(f"[save_to_db] Track {track.id} saved — {len(state['syllabus'])} days")
        return {
            "track_id": track.id,
            "topic": state["topic"],
            "total_days": state["total_days"],
            "syllabus": state["syllabus"],
        }

    except Exception as e:
        db.rollback()
        print(f"[save_to_db] Failed: {e}")
        raise
    finally:
        db.close()
