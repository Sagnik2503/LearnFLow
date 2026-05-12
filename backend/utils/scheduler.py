from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from db.database import SessionLocal
from db.crud import (
    get_active_tracks_for_delivery,
    create_newsletter,
    advance_user_track_day,
)
from utils.create_newsletter import build_newsletter


def deliver_newsletters():
    """Find all tracks due at the current time, generate + save + "send"."""
    now = datetime.now().strftime("%H:%M")
    print(f"\n⏰ Scheduler check at {now}")

    db = SessionLocal()
    try:
        tracks = get_active_tracks_for_delivery(db, now)
        if not tracks:
            print(f"  📭 No tracks due at {now}")
            return

        for ut in tracks:
            day = ut.current_day
            print(f"  📬 Generating Day {day} for user_track {ut.id} (user={ut.user.email})")

            try:
                content = build_newsletter(db, ut.track_id, day)
                create_newsletter(db, ut.id, day, content)
                advance_user_track_day(db, ut.id)

                print(f"     ✅ Day {day} generated & sent to {ut.user.email}")

                if ut.current_day > ut.total_days:
                    print(f"     🎉 Track {ut.id} complete for {ut.user.email}")

            except Exception as e:
                print(f"     ❌ Failed for user_track {ut.id}: {e}")

    finally:
        db.close()


scheduler = BackgroundScheduler()

scheduler.add_job(
    deliver_newsletters,
    trigger="cron",
    minute="*",
    id="deliver_newsletters",
)

scheduler.start()
print("🚀 Scheduler started — checking every minute for due deliveries")
