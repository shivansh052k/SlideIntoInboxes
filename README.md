<div align="center">

# SlideIntoInboxes

**A full-stack email automation dashboard — built for job hunters, recruiters, and anyone who sends personalized bulk emails at scale.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

> Pull contacts from Google Sheets → customize your email template → select recipients → schedule independent jobs → track everything from a sleek dark dashboard.

</div>

---

## 📸 Overview

SlideIntoInboxes turns a tedious manual outreach process into a point-and-click workflow. It connects directly to your Google Sheet of contacts, lets you edit your email template live in the browser, and gives you full control over when and to whom emails are sent — with a live job tracker to follow along.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **Recipients Dashboard** | View all contacts pulled from Google Sheets with sent/pending status badges |
| ☑️ **Checkbox Selection** | Select individual or all recipients for targeted scheduling |
| 👁 **Live Email Preview** | See exactly how your email looks before sending, rendered in a sandboxed iframe |
| ✏️ **WYSIWYG Editor** | Edit email content directly in the browser — bold, italic, underline, font, size, color, alignment |
| ⚡ **Send Now** | Blast emails to all pending recipients instantly |
| 🕐 **Multi-Job Scheduling** | Schedule multiple independent jobs at different times for different recipient groups |
| 🗓 **Jobs Tracker** | Live-updating jobs table with status badges (Scheduled / Running / Finished / Failed) |
| 🔍 **Expandable Job Details** | Click any job to reveal its full recipient list and execution logs |
| 📬 **Sent Log** | Full history of every sent email with message IDs and one-click log reset |
| 📎 **Resume Attachment** | Automatically attaches a PDF to every outgoing email |
| 🔒 **Secrets via `.env`** | All credentials stored locally — never hardcoded, never committed |

---

## 🏗 Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                           │
│   React 18 · Vite · React Router · Axios               │
├─────────────────────────────────────────────────────────┤
│                      Backend                            │
│   FastAPI · Uvicorn · APScheduler · python-dotenv      │
├─────────────────────────────────────────────────────────┤
│                   Integrations                          │
│   Google Sheets API (gspread) · Gmail SMTP (SSL 465)   │
│   Google Service Account · fuzzywuzzy (name matching)  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Auto_Emailer_Application/
│
├── backend/
│   ├── main.py                # FastAPI app & all REST endpoints
│   ├── emailer.py             # Core email logic, Google Sheets, SMTP
│   ├── scheduler_manager.py   # Multi-job APScheduler singleton
│   ├── email_template.html    # HTML email template (editable from dashboard)
│   ├── requirements.txt
│   ├── .env                   # 🔒 Your secrets (gitignored)
│   └── .env.example           # Template — copy this to .env
│
├── frontend/
│   └── src/
│       ├── App.jsx            # Router, shared state, nav
│       ├── App.css            # Full dark theme design system
│       ├── api.js             # Axios API calls
│       └── pages/
│           ├── Recipients.jsx # Contacts table with checkboxes
│           ├── Preview.jsx    # Email preview + WYSIWYG editor
│           ├── Schedule.jsx   # Send now + schedule jobs
│           ├── Jobs.jsx       # Live job tracker with expandable rows
│           └── SentLog.jsx    # Sent email history
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Cloud project with the **Sheets API** and **Drive API** enabled
- A Google **Service Account** with access to your contacts spreadsheet
- A Gmail account with an **App Password** generated ([instructions](https://support.google.com/accounts/answer/185833))

---

### 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/emailer.git
cd emailer
```

---

### 2 — Configure secrets

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your values:

```env
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_16_char_app_password
CREDS_FILE=/absolute/path/to/your/service-account.json
RESUME_PATH=/absolute/path/to/your/resume.pdf
SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/
CONTACTS_GID=your_contacts_tab_gid
INTERNSHIPS_GID=your_jobs_tab_gid
```

> **What is a GID?** Open your Google Sheet → click a tab at the bottom → the URL will show `gid=XXXXXXXXXX`. That number is the GID.

---

### 3 — Set up the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive API explorer.

---

### 4 — Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`. Open it in your browser.

---

## 🗺 How to Use

### Sending to everyone right now
1. Go to **Run & Schedule**
2. Click **Send All Emails Now**
3. Watch the live log output

### Scheduling targeted jobs
1. Go to **Recipients** → check the people you want to email
2. A floating action bar appears — click **Schedule Selected →**
3. On the **Run & Schedule** page, pick a date & time → click **Create Job**
4. Go to **Jobs** to track status live (auto-refreshes every 5 seconds)

Repeat from step 1 to schedule a second independent job for a different group at a different time.

### Editing your email template
1. Go to **Preview**
2. Click **Edit** — the email becomes directly editable
3. Use the formatting toolbar (bold, font, color, alignment...)
4. Click **Save** — the template is updated on the server immediately

### Managing sent history
1. Go to **Sent Log** to see every email with its message ID
2. Click **Clear Log** to reset the sent tracker (this allows re-sending to the same addresses)

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/recipients` | All contacts with sent status |
| `GET` | `/preview` | Current HTML email template |
| `PUT` | `/preview` | Save edited template |
| `POST` | `/send` | Send to all pending recipients now |
| `POST` | `/jobs` | Create a scheduled job for selected recipients |
| `GET` | `/jobs` | List all jobs (summary) |
| `GET` | `/jobs/{id}` | Full job detail + logs |
| `DELETE` | `/jobs/{id}` | Cancel a scheduled job |
| `GET` | `/sent` | Sent email log |
| `DELETE` | `/sent` | Clear sent log |

---

## 🔒 Security Notes

- **Credentials never leave your machine.** `backend/.env` is gitignored.
- The Google service account JSON is referenced by path, not bundled.
- Gmail App Passwords are scoped — they can be revoked independently of your main account password.
- The CORS policy restricts API access to `localhost:5173` only.

---

## 🗺 Google Sheet Format

Your **Contacts** sheet should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `Email` | ✅ | Recipient email address |
| `Company` | ✅ | Company name (used for subject line) |
| `First Name` | | Personalization |
| `Position` | | Their role at the company |
| `Status` | | Job role you're applying for (default: `AI/ML Engineer`) |
| `Summary` | | Brief company/role note |
| `link` | | Direct job posting URL |

Your **Internships/Jobs** sheet should have:

| Column | Required | Description |
|--------|----------|-------------|
| `Company` | ✅ | Company name (fuzzy-matched to contacts) |
| `Link` | | Job posting URL |
| `Status` | | Role title |

> If a contact doesn't have a direct `link`, Emailer fuzzy-matches their company name to the jobs sheet to auto-fill the link.

---

## 🧠 How Scheduling Works

Each job is an independent APScheduler `DateTrigger` task:

```
Create Job  →  unique job_id generated
               recipient snapshot stored in memory
               status: "scheduled"
                    ↓
At run_at   →  status: "running"
               emails sent one by one
                    ↓
Done        →  status: "finished" or "failed"
               logs captured per job
```

Jobs persist in memory for the life of the backend process. If you restart the server, in-memory jobs are lost (emails already sent are still tracked in `sent_emails.txt`).

---

## 🛠 Troubleshooting

**Backend won't start**
→ Make sure `backend/.env` exists and all values are filled in.

**`ModuleNotFoundError`**
→ Run `pip install -r backend/requirements.txt` in your Python environment.

**Google Sheets returns empty / auth error**
→ Make sure your service account email is added as an **Editor** on the Google Sheet.

**Emails not sending**
→ Gmail App Password must be generated with 2FA enabled. Regular passwords won't work.

**Preview page blank**
→ Make sure `backend/email_template.html` exists and `uvicorn` is running.

---

## 📄 License

MIT — do whatever you want with it.

---

<div align="center">

Built with way too much caffeine and a lot of job applications to send.

**[⭐ Star this repo](../../)** if it saved you time!

</div>
