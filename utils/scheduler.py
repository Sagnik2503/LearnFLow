from apscheduler.schedulers.background import BackgroundScheduler
from test_email import run_test

scheduler = BackgroundScheduler()

scheduler.add_job(run_test, trigger="cron", hour=9, minute=0)  # 9 AM daily

scheduler.start()
