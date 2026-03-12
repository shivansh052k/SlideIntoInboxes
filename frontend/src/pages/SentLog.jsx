import { useEffect, useState } from "react"
import { getSent, clearSent } from "../api"

export default function SentLog() {
  const [sent, setSent]       = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    getSent()
      .then(res => setSent(res.data))
      .catch(() => setError("Failed to load sent log"))
      .finally(() => setLoading(false))
  }, [])

  function handleClear() {
    clearSent().then(() => setSent([]))
  }

  if (loading) return <p className="loading">Loading sent log...</p>
  if (error)   return <p className="error-msg">{error}</p>

  return (
    <div>
      <div className="page-header" style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
        <div>
          <h1>Sent Log</h1>
          <p>{sent.length} emails sent so far</p>
        </div>
        {sent.length > 0 && (
          <button className="btn btn-danger" onClick={handleClear}>Clear Log</button>
        )}
      </div>

      {sent.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">📭</div>
          <p>No emails sent yet.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Message ID</th>
              </tr>
            </thead>
            <tbody>
              {sent.map((s, i) => (
                <tr key={i}>
                  <td>{s.email}</td>
                  <td style={{ color:"var(--muted)", fontFamily:"monospace", fontSize:"11px" }}>{s.message_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
