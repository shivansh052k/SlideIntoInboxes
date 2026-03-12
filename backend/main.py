from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import emailer
import scheduler_manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── MODELS ────────────────────────────────────────────────────
class ScheduleJobRequest(BaseModel):
    run_at:     str        # ISO datetime string
    recipients: List[dict] # snapshot of selected recipients


class TemplateRequest(BaseModel):
    html: str


# ── RECIPIENTS ────────────────────────────────────────────────
@app.get("/recipients")
def get_recipients():
    recipients  = emailer.build_recipients()
    sent_emails = emailer.load_sent_emails()
    for r in recipients:
        r["sent"] = r["email"] in sent_emails
    return recipients


# ── SENT LOG ──────────────────────────────────────────────────
@app.get("/sent")
def get_sent():
    sent = emailer.load_sent_emails()
    return [{"email": k, "message_id": v} for k, v in sent.items()]

@app.delete("/sent")
def clear_sent():
    open(emailer.SENT_FILE, "w").close()
    return {"cleared": True}


# ── PREVIEW / TEMPLATE ────────────────────────────────────────
@app.get("/preview")
def get_preview():
    return {"html": emailer.get_email_body()}

@app.put("/preview")
def save_preview(body: TemplateRequest):
    with open(emailer.TEMPLATE_FILE, "w") as f:
        f.write(body.html)
    return {"saved": True}


# ── SEND NOW ──────────────────────────────────────────────────
@app.post("/send")
def send_emails():
    logs    = []
    results = emailer.run_emailer(log_callback=lambda msg: logs.append(msg))
    sent    = sum(1 for r in results if r.get("result") == "sent")
    skipped = sum(1 for r in results if r.get("result") == "skipped")
    failed  = sum(1 for r in results if r.get("result", "").startswith("failed"))
    return {"logs": logs, "sent": sent, "skipped": skipped, "failed": failed}


# ── JOBS (multi-schedule) ─────────────────────────────────────
@app.post("/jobs")
def create_job(body: ScheduleJobRequest):
    run_at = datetime.fromisoformat(body.run_at)
    if run_at <= datetime.now():
        raise HTTPException(status_code=400, detail="Please pick a future date and time.")
    job_id = scheduler_manager.schedule_job(run_at, body.recipients, emailer.run_emailer_for)
    return {"job_id": job_id, "scheduled_for": run_at.isoformat()}

@app.get("/jobs")
def list_jobs():
    return scheduler_manager.list_jobs()

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = scheduler_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.delete("/jobs/{job_id}")
def cancel_job(job_id: str):
    cancelled = scheduler_manager.cancel_job(job_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail="Job not found or already running/finished")
    return {"cancelled": True}
