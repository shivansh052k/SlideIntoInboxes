import gspread
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.service_account import Credentials
from fuzzywuzzy import process
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ── CONFIG ────────────────────────────────────────────────────
SCOPE       = ["https://www.googleapis.com/auth/spreadsheets",
               "https://www.googleapis.com/auth/drive"]
CREDS_FILE  = os.environ["CREDS_FILE"]
GMAIL_USER  = os.environ["GMAIL_USER"]
GMAIL_PASS  = os.environ["GMAIL_PASS"]
RESUME_PATH = os.environ["RESUME_PATH"]
SENT_FILE   = os.path.join(os.path.dirname(__file__), "..", "sent_emails.txt")

SHEET_URL       = os.environ["SHEET_URL"]
CONTACTS_GID    = os.environ["CONTACTS_GID"]
INTERNSHIPS_GID = os.environ["INTERNSHIPS_GID"]


# ── EMAIL BODY ────────────────────────────────────────────────
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "email_template.html")

def get_email_body():
    with open(TEMPLATE_FILE, "r") as f:
        return f.read()


# ── GOOGLE SHEET HELPERS ──────────────────────────────────────
def _auth():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
    return gspread.authorize(creds)

def load_sheet(gid):
    gc = _auth()
    ss = gc.open_by_url(SHEET_URL)
    for ws in ss.worksheets():
        if str(ws.id) == gid:
            return ws.get_all_records(expected_headers=ws.row_values(1))
    raise ValueError(f"Sheet with gid '{gid}' not found")

def get_contacts():
    return load_sheet(CONTACTS_GID)

def get_internships():
    return load_sheet(INTERNSHIPS_GID)


# ── SENT EMAIL TRACKING ───────────────────────────────────────
def load_sent_emails():
    sent = {}
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            for line in f.read().splitlines():
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    sent[parts[0]] = parts[1]
    return sent

def mark_sent(email, message_id):
    with open(SENT_FILE, "a") as f:
        f.write(f"{email},{message_id}\n")
        

# ── COMPANY MATCHING ──────────────────────────────────────────
def get_closest_match(company, company_list):
    result = process.extractOne(company, company_list)
    return result[0] if result and result[1] >= 80 else None


# ── BUILD RECIPIENT LIST ──────────────────────────────────────
def build_recipients():
    contacts    = get_contacts()
    internships = get_internships()
    internship_dict = {r["Company"]: [r["Link"], r["Status"], "", ""] for r in internships}

    recipients = []
    for record in contacts:
        try:
            company  = record["Company"].strip()
            email    = record["Email"].strip()
            name     = record.get("First Name", "").strip()
            position = record.get("Position", "").strip()
            summary  = record.get("Summary", "").strip()
            link     = record.get("link", "").strip()
            status   = record.get("Status", "AI/ML Engineer").strip()

            if link:
                internship_link = link
                job_status      = status
                job_summary     = summary
            else:
                matched = get_closest_match(company, list(internship_dict.keys()))
                if matched:
                    internship_link = internship_dict[matched][0]
                    job_status      = internship_dict[matched][1]
                    job_summary     = internship_dict[matched][2]
                else:
                    internship_link = ""
                    job_status      = "AI/ML Engineer"
                    job_summary     = ""

            recipients.append({
                "company":         company,
                "email":           email,
                "name":            name or "there",
                "position":        position or "employee",
                "internship_link": internship_link,
                "status":          job_status,
                "summary":         job_summary,
            })
        except Exception:
            continue

    return recipients


# ── SEND A SINGLE EMAIL ───────────────────────────────────────
def send_single_email(subject, html_body, recipient_email):
    msg = MIMEMultipart("related")
    msg["From"]    = f"Shivansh Gupta <{GMAIL_USER}>"
    msg["To"]      = recipient_email
    msg["Subject"] = subject
    message_id     = f"<{uuid.uuid4()}>"

    msg.attach(MIMEText(html_body, "html"))

    with open(RESUME_PATH, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=Shivansh_Gupta_Resume.pdf")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

    return message_id

# ── SEND TO A SPECIFIC LIST OF RECIPIENTS ────────────────────
def run_emailer_for(recipients: list, log_callback=None):
    """Send emails only to the provided recipients list."""
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    sent_emails = load_sent_emails()
    results     = []

    for r in recipients:
        email = r["email"]

        if email in sent_emails:
            log(f"⏩ Skipping {email} — already sent")
            results.append({**r, "result": "skipped"})
            continue

        subject   = f"Application/Consideration for {r['status']} at {r['company']}"
        html_body = get_email_body().format(
            recipient_name  = r["name"],
            company_name    = r["company"],
            status          = r["status"],
            internship_link = r["internship_link"],
            position        = r["position"],
            summary         = r["summary"],
        )

        try:
            message_id = send_single_email(subject, html_body, email)
            mark_sent(email, message_id)
            log(f"✅ Sent → {email} ({r['company']})")
            results.append({**r, "result": "sent"})
        except Exception as e:
            log(f"❌ Failed → {email}: {e}")
            results.append({**r, "result": f"failed: {e}"})

    return results


# ── MAIN RUN ──────────────────────────────────────────────────
def run_emailer(log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    sent_emails = load_sent_emails()
    recipients  = build_recipients()
    results     = []

    for r in recipients:
        email = r["email"]

        if email in sent_emails:
            log(f"⏩ Skipping {email} — already sent")
            results.append({**r, "result": "skipped"})
            continue

        subject   = f"Application/Consideration for {r['status']} at {r['company']}"
        html_body = get_email_body().format(
            recipient_name  = r["name"],
            company_name    = r["company"],
            status          = r["status"],
            internship_link = r["internship_link"],
            position        = r["position"],
            summary         = r["summary"],
        )

        try:
            # email="spartangamingextreme@gmail.com"
            message_id = send_single_email(subject, html_body, email)
            mark_sent(email, message_id)
            log(f"✅ Sent → {email} ({r['company']})")
            results.append({**r, "result": "sent"})
        except Exception as e:
            log(f"❌ Failed → {email}: {e}")
            results.append({**r, "result": f"failed: {e}"})

    return results