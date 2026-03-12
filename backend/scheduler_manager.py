from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import datetime

# Module-level singleton — persists across Streamlit reruns
_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.start()
    return _scheduler

def schedule_job(run_at: datetime.datetime, job_func):
    """Schedule job_func to run once at run_at. Replaces any existing scheduled job."""
    scheduler = get_scheduler()
    job = scheduler.add_job(
        job_func,
        trigger=DateTrigger(run_date=run_at),
        id="email_job",
        replace_existing=True,
    )
    return job

def get_scheduled_job():
    """Returns the current scheduled job, or None."""
    return get_scheduler().get_job("email_job")

def cancel_job():
    """Cancels the scheduled job. Returns True if it existed."""
    job = get_scheduler().get_job("email_job")
    if job:
        job.remove()
        return True
    return False