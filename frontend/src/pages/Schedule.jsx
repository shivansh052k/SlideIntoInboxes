import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { sendEmails, postJob } from "../api"

export default function Schedule({ selected, setSelected }) {
  const [sending, setSending] = useState(false)
  const [result, setResult]   = useState(null)
  const [runAt, setRunAt]     = useState("")
  const [schedMsg, setSchedMsg] = useState(null)
  const [scheduling, setScheduling] = useState(false)
  const navigate = useNavigate()

  function handleSendNow() {
    setSending(true)
    setResult(null)
    sendEmails()
      .then(res => setResult(res.data))
      .finally(() => setSending(false))
  }

  function handleScheduleJob() {
    if (!runAt) return
    if (selected.length === 0) {
      setSchedMsg({ error: true, text: "No recipients selected. Go to Recipients and select some first." })
      return
    }
    setScheduling(true)
    setSchedMsg(null)
    postJob(runAt, selected)
      .then(res => {
        setSchedMsg({ error: false, text: `Job ${res.data.job_id} scheduled for ${res.data.scheduled_for}` })
        setSelected([])
        setRunAt("")
        setTimeout(() => navigate("/jobs"), 1200)
      })
      .catch(err => {
        const msg = err.response?.data?.detail || "Failed to schedule job"
        setSchedMsg({ error: true, text: msg })
      })
      .finally(() => setScheduling(false))
  }

  return (
    <div>
      <div className="page-header">
        <h1>Run & Schedule</h1>
        <p>Send all emails now, or schedule a targeted job for later</p>
      </div>

      {/* Send Now */}
      <div className="card">
        <h3>⚡ Send Now</h3>
        <p style={{ color:"var(--muted)", fontSize:"13px", marginBottom:"14px" }}>
          Sends to all pending recipients immediately.
        </p>
        <button className="btn btn-primary" onClick={handleSendNow} disabled={sending}>
          {sending ? "Sending..." : "Send All Emails Now"}
        </button>
        {result && (
          <>
            <div className="result-banner">
              <span><div className="num green">{result.sent}</div><div className="label">Sent</div></span>
              <span><div className="num yellow">{result.skipped}</div><div className="label">Skipped</div></span>
              <span><div className="num red">{result.failed}</div><div className="label">Failed</div></span>
            </div>
            <pre className="logbox">{result.logs.join("\n")}</pre>
          </>
        )}
      </div>

      {/* Schedule Job */}
      <div className="card">
        <h3>🕐 Schedule a Job</h3>

        {selected.length === 0 ? (
          <div style={{ display:"flex", alignItems:"center", gap:"12px", padding:"14px 0" }}>
            <span style={{ color:"var(--muted)", fontSize:"13px" }}>No recipients selected.</span>
            <button className="btn btn-ghost" onClick={() => navigate("/")}>← Select Recipients</button>
          </div>
        ) : (
          <>
            <div className="selected-summary">
              <div className="selected-summary-header">
                <span>{selected.length} recipient{selected.length !== 1 ? "s" : ""} selected</span>
                <button className="btn btn-ghost" style={{ padding:"2px 10px", fontSize:"12px" }} onClick={() => navigate("/")}>
                  Change
                </button>
              </div>
              <div className="table-wrap" style={{ marginTop:"10px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Company</th>
                      <th>Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.map((r, i) => (
                      <tr key={i}>
                        <td>{r.name}</td>
                        <td>{r.company}</td>
                        <td style={{ color:"#94a3b8" }}>{r.email}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div style={{ display:"flex", gap:"10px", alignItems:"center", flexWrap:"wrap", marginTop:"16px" }}>
              <input
                className="input"
                type="datetime-local"
                value={runAt}
                onChange={e => setRunAt(e.target.value)}
              />
              <button className="btn btn-primary" onClick={handleScheduleJob} disabled={scheduling || !runAt}>
                {scheduling ? "Scheduling..." : "Create Job"}
              </button>
            </div>
          </>
        )}

        {schedMsg && (
          <p className={schedMsg.error ? "error-msg" : "success-msg"} style={{ marginTop:"12px" }}>
            {schedMsg.text}
          </p>
        )}
      </div>
    </div>
  )
}
