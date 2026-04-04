import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal, init_db
from db.crud import get_or_create_user
from utils.create_newsletter import start_topic, get_today_newsletter
from utils.email import markdown_to_html, send_newsletter_email
from dotenv import load_dotenv

load_dotenv()
init_db()
db = SessionLocal()

USER_ID = 1
TOPIC = "recommendation algorithms"
EMAIL = os.getenv("TEST_MAIL")
APP_PW = os.getenv("EMAIL_APP_PASSWORD")
DELIVERY_TIME = "09:00"


def run_test():
    # 1. Start topic (only once)
    user_track = start_topic(db, USER_ID, TOPIC, DELIVERY_TIME)

    # 2. Get today's newsletter (this will generate it)
    content_md = get_today_newsletter(db, USER_ID, user_track.track_id)

    print("\n=== GENERATED MARKDOWN ===\n")
    print(content_md[:500])  # preview

    # 3. Send email
    send_newsletter_email(
        to_email=EMAIL,
        subject="Day 1: Why Your Feed Knows You Better Than You Know Yourself",
        markdown_content=content_md,
    )
    print("\n✅ Email sent! Check your inbox.")


if __name__ == "__main__":
    run_test()
