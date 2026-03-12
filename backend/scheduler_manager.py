from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import datetime
import uuid

_scheduler = None

# job_id → { run_at, recipients, status, logs }
_jobs: dict[str, dict] = {}


def get_scheduler():
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.start()
    return _scheduler


def schedule_job(run_at: datetime.datetime, recipients: list, email_func) -> str:
    """Schedule email_func(recipients) at run_at. Returns a unique job_id."""
    job_id = str(uuid.uuid4())[:8]

    _jobs[job_id] = {
        "job_id":     job_id,
        "run_at":     run_at.isoformat(),
        "recipients": recipients,
        "status":     "scheduled",
        "logs":       [],
    }

    def run():
        _jobs[job_id]["status"] = "running"
        logs = []
        try:
            email_func(recipients, log_callback=lambda m: logs.append(m))
            _jobs[job_id]["status"] = "finished"
        except Exception as e:
            _jobs[job_id]["status"] = "failed"
            logs.append(f"Job error: {e}")
        _jobs[job_id]["logs"] = logs

    get_scheduler().add_job(
        run,
        trigger=DateTrigger(run_date=run_at),
        id=job_id,
    )
    return job_id


def list_jobs() -> list[dict]:
    """Return all jobs (metadata only, no logs)."""
    result = []
    for j in _jobs.values():
        result.append({
            "job_id":          j["job_id"],
            "run_at":          j["run_at"],
            "recipient_count": len(j["recipients"]),
            "status":          j["status"],
        })
    return result


def get_job(job_id: str) -> dict | None:
    """Return full job details including recipients and logs."""
    return _jobs.get(job_id)


def cancel_job(job_id: str) -> bool:
    """Cancel a scheduled job. Returns True if it existed and was scheduled."""
    job = _jobs.get(job_id)
    if not job:
        return False
    if job["status"] == "scheduled":
        try:
            get_scheduler().remove_job(job_id)
        except Exception:
            pass
        del _jobs[job_id]
        return True
    return False
