from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from db.database import init_db, SessionLocal
from db.crud import get_syllabus, get_track, get_or_create_user, create_subscription, unsubscribe
from schema.schemas import SubscribeRequest, SubscribeResponse
from graphs.builder.curriculum_builder import run_curriculum_graph

import os

# ── Init ────────────────────────────────────────────
init_db()

app = FastAPI(title="LearnFlow API", version="0.1.0")

# CORS – allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve frontend static files ────────────────────
FRONTEND_DIR = os.path.abspath("frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


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


# ── Routes ─────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LearnFlow API is running. Frontend not found."}


@app.post("/api/subscribe", response_model=SubscribeResponse)
async def subscribe(req: SubscribeRequest):
    """Subscribe to daily newsletters for a topic."""
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


@app.post("/api/unsubscribe/{user_track_id}")
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
                description=None,
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


@app.get("/api/newsletter/{track_id}/{day}")
async def get_newsletter_for_day(track_id: int, day: int):
    """Generate or retrieve a newsletter for a specific day of a track."""
    from graphs.builder.newsletter_builder import run_newsletter_graph
    from db.crud import get_previous_title

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

        prev_title = get_previous_title(db, track_id, day)

        content = run_newsletter_graph(
            topic=track.topic,
            item={
                "day": syllabus_item.day,
                "title": syllabus_item.title,
                "description": "",
                "concepts": syllabus_item.concepts,
            },
            previous=prev_title,
            day=day,
            total_days=track.total_days,
        )

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
