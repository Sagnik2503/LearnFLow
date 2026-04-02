from db.database import SessionLocal
from utils.create_newsletter import start_topic, get_today_newsletter
from utils.email import markdown_to_html, send_newsletter_email
import os
from dotenv import load_dotenv

load_dotenv()
db = SessionLocal()

USER_ID = "test_user"
TOPIC = "F1 rules"
EMAIL = os.getenv("TEST_MAIL")
APP_PW = os.getenv("EMAIL_APP_PASSWORD")


def run_test():
    # 1. Start topic (only once)
    user_track = start_topic(db, USER_ID, TOPIC)

    # 2. Get today's newsletter (this will generate it)
    content_md = get_today_newsletter(db, USER_ID, user_track.track_id)

    print("\n=== GENERATED MARKDOWN ===\n")
    print(content_md[:500])  # preview

    # 3. Convert to HTML
    html_content = markdown_to_html(content_md)

    # 4. Send email
    send_newsletter_email(
        to_email=EMAIL,
        subject="Day 1: F1 rules: How it works!",
        markdown_content=content_md,
    )
    print("\n✅ Email sent! Check your inbox.")


if __name__ == "__main__":
    run_test()
