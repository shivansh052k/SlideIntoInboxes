import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getRecipients } from "../api"

export default function Recipients({ selected, setSelected }) {
  const [recipients, setRecipients] = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getRecipients()
      .then(res => setRecipients(res.data))
      .catch(() => setError("Failed to load recipients"))
      .finally(() => setLoading(false))
  }, [])

  const sent    = recipients.filter(r => r.sent).length
  const pending = recipients.filter(r => !r.sent).length

  function toggleOne(r) {
    const exists = selected.find(s => s.email === r.email)
    if (exists) setSelected(selected.filter(s => s.email !== r.email))
    else         setSelected([...selected, r])
  }

  function toggleAll() {
    if (selected.length === recipients.length) setSelected([])
    else setSelected([...recipients])
  }

  function isSelected(r) {
    return !!selected.find(s => s.email === r.email)
  }

  if (loading) return <p className="loading">Loading recipients...</p>
  if (error)   return <p className="error-msg">{error}</p>

  return (
    <div style={{ paddingBottom: selected.length > 0 ? "90px" : "0" }}>
      <div className="page-header">
        <h1>Recipients</h1>
        <p>Select contacts to schedule a targeted email job</p>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="stat-value">{recipients.length}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat">
          <div className="stat-value green">{sent}</div>
          <div className="stat-label">Sent</div>
        </div>
        <div className="stat">
          <div className="stat-value yellow">{pending}</div>
          <div className="stat-label">Pending</div>
        </div>
        <div className="stat">
          <div className="stat-value" style={{ color:"var(--accent)" }}>{selected.length}</div>
          <div className="stat-label">Selected</div>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th style={{ width:"40px" }}>
                <input
                  type="checkbox"
                  checked={selected.length === recipients.length && recipients.length > 0}
                  onChange={toggleAll}
                  style={{ cursor:"pointer", accentColor:"var(--accent)" }}
                />
              </th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Full Name</th>
              <th>Position</th>
              <th>Company</th>
              <th>Email</th>
              <th>Role</th>
              <th>Link</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {recipients.map((r, i) => (
              <tr
                key={i}
                onClick={() => toggleOne(r)}
                style={{ cursor:"pointer", background: isSelected(r) ? "rgba(99,102,241,0.08)" : undefined }}
              >
                <td onClick={e => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={isSelected(r)}
                    onChange={() => toggleOne(r)}
                    style={{ cursor:"pointer", accentColor:"var(--accent)" }}
                  />
                </td>
                <td>{r.first_name || "—"}</td>
                <td>{r.last_name || "—"}</td>
                <td>{[r.first_name, r.last_name].filter(Boolean).join(" ") || "—"}</td>
                <td style={{ color:"#94a3b8" }}>{r.position || "—"}</td>
                <td>{r.company}</td>
                <td style={{ color:"#94a3b8", fontSize:"0.85em" }}>{r.email}</td>
                <td style={{ color:"#94a3b8" }}>{r.status || "—"}</td>
                <td>
                  {r.internship_link
                    ? <a href={r.internship_link} target="_blank" rel="noreferrer" style={{ color:"var(--accent)", background:"rgba(99,102,241,0.12)", padding:"2px 8px", borderRadius:"4px", fontSize:"0.8em", fontWeight:600, textDecoration:"none", whiteSpace:"nowrap" }} onClick={e => e.stopPropagation()}>Link ↗</a>
                    : "—"}
                </td>
                <td>
                  <span className={`badge ${r.sent ? "badge-sent" : "badge-pending"}`}>
                    {r.sent ? "✓ Sent" : "● Pending"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected.length > 0 && (
        <div className="action-bar">
          <span className="action-bar-count">{selected.length} recipient{selected.length !== 1 ? "s" : ""} selected</span>
          <div style={{ display:"flex", gap:"10px" }}>
            <button className="btn btn-ghost" onClick={() => setSelected([])}>Clear</button>
            <button className="btn btn-primary" onClick={() => navigate("/schedule")}>
              Schedule Selected →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
