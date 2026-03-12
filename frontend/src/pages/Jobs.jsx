import { useEffect, useState } from "react"
import { getJobs, getJob, deleteJob } from "../api"

const STATUS_CLASS = {
  scheduled: "badge-pending",
  running:   "badge-running",
  finished:  "badge-sent",
  failed:    "badge-failed",
}

const STATUS_LABEL = {
  scheduled: "● Scheduled",
  running:   "⟳ Running",
  finished:  "✓ Finished",
  failed:    "✕ Failed",
}

export default function Jobs() {
  const [jobs, setJobs]         = useState([])
  const [loading, setLoading]   = useState(true)
  const [expanded, setExpanded] = useState(null)   // job_id of open row
  const [detail, setDetail]     = useState({})     // job_id → full detail

  function fetchJobs() {
    getJobs()
      .then(res => setJobs(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchJobs()
    const id = setInterval(fetchJobs, 5000)
    return () => clearInterval(id)
  }, [])

  function toggleRow(job_id) {
    if (expanded === job_id) {
      setExpanded(null)
      return
    }
    setExpanded(job_id)
    if (!detail[job_id]) {
      getJob(job_id).then(res => setDetail(prev => ({ ...prev, [job_id]: res.data })))
    }
  }

  function handleCancel(e, job_id) {
    e.stopPropagation()
    deleteJob(job_id).then(() => {
      setJobs(jobs.filter(j => j.job_id !== job_id))
      if (expanded === job_id) setExpanded(null)
    })
  }

  function fmt(iso) {
    return new Date(iso).toLocaleString(undefined, {
      month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit",
    })
  }

  if (loading) return <p className="loading">Loading jobs...</p>

  return (
    <div>
      <div className="page-header" style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
        <div>
          <h1>Jobs</h1>
          <p>{jobs.length} scheduled job{jobs.length !== 1 ? "s" : ""}</p>
        </div>
        <button className="btn btn-ghost" onClick={fetchJobs}>Refresh</button>
      </div>

      {jobs.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">🗓</div>
          <p>No jobs yet. Select recipients and schedule a job.</p>
        </div>
      ) : (
        <div className="jobs-list">
          {jobs.map(job => (
            <div key={job.job_id} className="job-card">
              {/* ── Summary row ─────────────────────────── */}
              <div className="job-row" onClick={() => toggleRow(job.job_id)}>
                <div className="job-row-left">
                  <span className="job-id"># {job.job_id}</span>
                  <span className="job-time">{fmt(job.run_at)}</span>
                  <span className="job-count">{job.recipient_count} recipient{job.recipient_count !== 1 ? "s" : ""}</span>
                </div>
                <div className="job-row-right">
                  <span className={`badge ${STATUS_CLASS[job.status] || "badge-pending"}`}>
                    {STATUS_LABEL[job.status] || job.status}
                  </span>
                  {job.status === "scheduled" && (
                    <button
                      className="btn btn-danger"
                      style={{ padding:"4px 12px", fontSize:"12px" }}
                      onClick={e => handleCancel(e, job.job_id)}
                    >
                      Cancel
                    </button>
                  )}
                  <span className="expand-arrow">{expanded === job.job_id ? "▲" : "▼"}</span>
                </div>
              </div>

              {/* ── Expanded detail ──────────────────────── */}
              {expanded === job.job_id && (
                <div className="job-detail">
                  {!detail[job.job_id] ? (
                    <p className="loading" style={{ padding:"12px" }}>Loading details...</p>
                  ) : (
                    <>
                      <div className="table-wrap" style={{ marginBottom:"0" }}>
                        <table>
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Company</th>
                              <th>Email</th>
                              <th>Role</th>
                            </tr>
                          </thead>
                          <tbody>
                            {detail[job.job_id].recipients.map((r, i) => (
                              <tr key={i}>
                                <td>{r.name}</td>
                                <td>{r.company}</td>
                                <td style={{ color:"#94a3b8" }}>{r.email}</td>
                                <td style={{ color:"var(--muted)", fontSize:"12px" }}>{r.status}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {detail[job.job_id].logs?.length > 0 && (
                        <pre className="logbox" style={{ marginTop:"12px" }}>
                          {detail[job.job_id].logs.join("\n")}
                        </pre>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
