import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.database import init_db, SessionLocal
from db.crud import get_syllabus, get_track, get_or_create_user, create_subscription, unsubscribe
from graphs.builder.curriculum_builder import run_curriculum_graph
from schema.schemas import SubscribeRequest, SubscribeResponse

# ── Init ────────────────────────────────────────────
init_db()
app = FastAPI(title="LearnFlow API", version="0.1.0")

# CORS – configurable via FRONTEND_URL env var
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
if FRONTEND_URL:
    origins = [FRONTEND_URL]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────
class GenerateSyllabusRequest(BaseModel):
    topic: str
    email: str | None = None
 

class SyllabusItemResponse(BaseModel):
    day: int
    title: str
    description: str | None = None
    concepts: list[str]


class SyllabusResponse(BaseModel):
    track_id: int
    topic: str
    total_days: int
    syllabus: list[SyllabusItemResponse]


class UnsubscribeResponse(BaseModel):
    message: str


class NewsletterResponse(BaseModel):
    day: int
    title: str
    content: str


# ── API Routes ─────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "LearnFlow API is running"}


@app.post("/api/subscribe", response_model=SubscribeResponse)
async def subscribe(req: SubscribeRequest):
    """Subscribe to daily newsletters for a topic."""
    print(f"📩 Subscribe request: email={req.email}, topic={req.topic}, time={req.delivery_time}")
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    if not req.email or not req.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        result = run_curriculum_graph(req.topic.strip())

        db = SessionLocal()
        try:
            user = get_or_create_user(db, req.email.strip())
            create_subscription(
                db,
                user_id=user.id,
                track_id=result["track_id"],
                total_days=result["total_days"],
                delivery_time=req.delivery_time,
            )
        finally:
            db.close()

        return SubscribeResponse(
            track_id=result["track_id"],
            topic=result["topic"],
            total_days=result["total_days"],
            message=f"Subscribed! You'll receive daily newsletters at {req.delivery_time}",
        )

    except Exception as e:
        print(f"❌ Subscription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/unsubscribe/{user_track_id}", response_model=UnsubscribeResponse)
async def unsubscribe_endpoint(user_track_id: int):
    """Unsubscribe from a track."""
    db = SessionLocal()
    try:
        result = unsubscribe(db, user_track_id)
        if not result:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return {"message": "Unsubscribed successfully"}
    finally:
        db.close()


@app.post("/api/generate-syllabus", response_model=SyllabusResponse)
async def generate_syllabus(req: GenerateSyllabusRequest):
    """Generate a multi-day syllabus for a given topic using the LLM curriculum graph."""
    print(f"📋 Generate syllabus: topic={req.topic}, email={req.email}")
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    try:
        result = run_curriculum_graph(req.topic.strip())

        syllabus_items = []
        for item in result["syllabus"]:
            syllabus_items.append(
                SyllabusItemResponse(
                    day=item["day"],
                    title=item["title"],
                    description=item.get("description"),
                    concepts=item["concepts"],
                )
            )

        return SyllabusResponse(
            track_id=result["track_id"],
            topic=result["topic"],
            total_days=result["total_days"],
            syllabus=syllabus_items,
        )

    except Exception as e:
        print(f"❌ Syllabus generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/syllabus/{track_id}", response_model=SyllabusResponse)
async def get_syllabus_by_track(track_id: int):
    """Retrieve a previously generated syllabus by track ID."""
    db = SessionLocal()
    try:
        track = get_track(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        items = get_syllabus(db, track_id)

        syllabus_items = [
            SyllabusItemResponse(
                day=item.day,
                title=item.title,
                description=item.description,
                concepts=item.concepts,
            )
            for item in items
        ]

        return SyllabusResponse(
            track_id=track.id,
            topic=track.topic,
            total_days=track.total_days,
            syllabus=syllabus_items,
        )
    finally:
        db.close()


@app.get("/api/newsletter/{track_id}/{day}", response_model=NewsletterResponse)
async def get_newsletter_for_day(track_id: int, day: int):
    """Generate or retrieve a newsletter for a specific day of a track."""
    from utils.create_newsletter import build_newsletter

    db = SessionLocal()
    try:
        track = get_track(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        items = get_syllabus(db, track_id)
        syllabus_item = next((i for i in items if i.day == day), None)

        if not syllabus_item:
            raise HTTPException(
                status_code=404, detail=f"No syllabus found for day {day}"
            )

        content = build_newsletter(db, track_id, day)

        return {"day": day, "title": syllabus_item.title, "content": content}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Newsletter generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
