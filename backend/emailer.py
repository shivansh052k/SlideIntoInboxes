import gspread
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.service_account import Credentials
from fuzzywuzzy import process
import os

# ── CONFIG ────────────────────────────────────────────────────
SCOPE       = ["https://www.googleapis.com/auth/spreadsheets",
               "https://www.googleapis.com/auth/drive"]
CREDS_FILE  = "/Users/shivansh052k/Downloads/Emailer/mailautomation-473721-fbddf2c244a7.json"
GMAIL_USER  = "shivanshgupta323@gmail.com"
GMAIL_PASS  = "idsu lzto jckp ywjb"
RESUME_PATH = "/Users/shivansh052k/Downloads/Emailer/Shivansh_Gupta_Resume.pdf"
SENT_FILE   = "/Users/shivansh052k/Downloads/Emailer/EmailerApp/Auto_Emailer_Application/sent_emails.txt"

SHEET_URL       = "https://docs.google.com/spreadsheets/d/1QwVDk4BFdWy_7wKKgBltnHBeMVz0pKclAGf-eSYalpQ/"
CONTACTS_GID    = "1200200492"
INTERNSHIPS_GID = "0"


# ── EMAIL BODY ────────────────────────────────────────────────
EMAIL_BODY = """
<html>
  <head>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <meta name="color-scheme" content="light only">
    <meta name="supported-color-schemes" content="light only">
  </head>
  <body style="margin:0; padding:0; background:#ffffff; font-family:'Roboto', Arial, Helvetica, sans-serif; line-height:1.6; color:#111;">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="width:100%;">
      <tr>
        <td align="center">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:900px; max-width:100%; padding:16px;">
            <tr>
              <td style="font-size:16px;">
                <p style="margin:0 0 16px 0;">Hi {recipient_name},</p>

                <p style="margin:0 0 14px 0;">
                  My name is <b>Shivansh Gupta</b>, and I am an ML Engineer specializing in architecting and
                  optimizing high-performance intelligent systems that bridge the gap between research and
                  real-world deployment. My work spans Applied ML, NLP, LLMs/RAG, RL, Recommender Systems,
                  and Agentic Workflows, driven by a goal to make AI systems more transparent, context-aware,
                  and aligned with real-world objectives.
                </p>

                <p style="margin:0 0 14px 0;">
                  Recently, I stumbled upon the <b>{status}</b> opportunity with <b>{company_name}</b> that
                  really resonated with my interests and my previous professional and research experience. {summary}
                </p>

                <p style="margin:0 0 14px 0;">
                  Given your position as the <b>{position}</b>, I believe you are the best person to evaluate
                  if my background fits your team's engineering culture and requirements.
                </p>

                <p style="margin:0 0 14px 0;">
                  I would be truly grateful for a referral if you believe my profile aligns. Alternatively,
                  forwarding my profile to the hiring team or pointing me toward the right contact would be
                  equally appreciated.
                </p>

                <p style="margin:0 0 14px 0;">
                  Additionally, if you are open to it, I would love to have a brief chat at your convenience
                  to discuss how my experience can contribute to the organization's success.
                </p>

                <p style="margin:0 0 16px 0;">
                  For your convenience, I have attached the specific job link and my credentials below:
                </p>

                <div style="margin:0 0 16px 0;">
                  <div><b>1. Job Link:</b> <a href="{internship_link}" target="_blank">{internship_link}</a></div>
                  <div><b>2. LinkedIn Profile:</b> <a href="https://www.linkedin.com/in/-shivansh-gupta/" target="_blank">https://www.linkedin.com/in/-shivansh-gupta/</a></div>
                  <div><b>3. Resume:</b> <a href="https://1drv.ms/b/c/3dc83b8b8cddf45d/IQCx9oLHsuarQZmY_LlC8dvmAfUC-U9TVSoE0fO9jbSw-Aw?e=fdnAz5" target="_blank">Shivansh_Gupta_Resume.pdf</a></div>
                </div>

                <p style="margin:14px 0 16px 0;">
                  I am confident I can bring this same focus on performance and real-world results to your
                  team at <b>{company_name}</b>. Looking forward to hearing from you.
                </p>

                <p style="margin:0;">
                  Best regards,<br>
                  <b>Shivansh Gupta</b><br>
                  <a href="https://www.linkedin.com/in/-shivansh-gupta/" target="_blank">LinkedIn</a> | +1 (716)-275-9685
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


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
        html_body = EMAIL_BODY.format(
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