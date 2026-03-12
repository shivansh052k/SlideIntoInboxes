import { useEffect, useRef, useState } from "react"
import axios from "axios"

export default function Preview() {
  const [html, setHtml]       = useState("")
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving]   = useState(false)
  const [saved, setSaved]     = useState(false)
  const iframeRef             = useRef(null)

  useEffect(() => {
    axios.get("http://localhost:8000/preview")
      .then(res => setHtml(res.data.html))
      .finally(() => setLoading(false))
  }, [])

  function enableEdit() {
    setEditing(true)
    setTimeout(() => {
      const doc = iframeRef.current?.contentDocument
      if (doc) doc.designMode = "on"
    }, 50)
  }

  function disableEdit() {
    const doc = iframeRef.current?.contentDocument
    if (doc) doc.designMode = "off"
    setEditing(false)
  }

  function execCmd(cmd, value = null) {
    iframeRef.current?.contentDocument?.execCommand(cmd, false, value)
    iframeRef.current?.contentWindow?.focus()
  }

  function handleSave() {
    const doc = iframeRef.current?.contentDocument
    if (!doc) return
    const updatedHtml = doc.documentElement.outerHTML
    setSaving(true)
    axios.put("http://localhost:8000/preview", { html: updatedHtml })
      .then(() => { setSaved(true); setTimeout(() => setSaved(false), 2000) })
      .finally(() => { setSaving(false); disableEdit() })
  }

  if (loading) return <p className="loading">Loading preview...</p>

  return (
    <div>
      <div className="page-header" style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
        <div>
          <h1>Email Preview</h1>
          <p>{editing ? "Click on any text to edit it directly." : "Read-only preview of your email template."}</p>
        </div>
        <div style={{ display:"flex", gap:"8px" }}>
          {editing ? (
            <>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button className="btn btn-ghost" onClick={disableEdit}>Cancel</button>
            </>
          ) : (
            <button className="btn btn-ghost" onClick={enableEdit}>Edit</button>
          )}
        </div>
      </div>

      {saved && <p className="success-msg" style={{ marginBottom:"12px" }}>Template saved!</p>}

      {editing && (
        <div className="card" style={{ padding:"10px 14px", marginBottom:"12px", display:"flex", gap:"6px", flexWrap:"wrap", alignItems:"center" }}>
          <button className="btn btn-ghost" style={{padding:"4px 10px", fontWeight:"bold"}}        onClick={() => execCmd("bold")}>B</button>
          <button className="btn btn-ghost" style={{padding:"4px 10px", fontStyle:"italic"}}       onClick={() => execCmd("italic")}>I</button>
          <button className="btn btn-ghost" style={{padding:"4px 10px", textDecoration:"underline"}} onClick={() => execCmd("underline")}>U</button>
          <div style={{ width:"1px", height:"24px", background:"var(--border)", margin:"0 4px" }} />
          <select className="input" style={{padding:"4px 8px"}} onChange={e => execCmd("fontName", e.target.value)}>
            <option value="Arial">Arial</option>
            <option value="Georgia">Georgia</option>
            <option value="Verdana">Verdana</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Courier New">Courier New</option>
          </select>
          <select className="input" style={{padding:"4px 8px"}} onChange={e => execCmd("fontSize", e.target.value)}>
            {[1,2,3,4,5,6,7].map(s => <option key={s} value={s}>{[10,13,16,18,24,32,48][s-1]}px</option>)}
          </select>
          <input type="color" title="Text color" style={{width:"32px", height:"32px", border:"none", background:"none", cursor:"pointer", padding:0}}
            onChange={e => execCmd("foreColor", e.target.value)} />
          <div style={{ width:"1px", height:"24px", background:"var(--border)", margin:"0 4px" }} />
          <button className="btn btn-ghost" style={{padding:"4px 10px"}} onClick={() => execCmd("justifyLeft")}>≡L</button>
          <button className="btn btn-ghost" style={{padding:"4px 10px"}} onClick={() => execCmd("justifyCenter")}>≡C</button>
          <button className="btn btn-ghost" style={{padding:"4px 10px"}} onClick={() => execCmd("justifyRight")}>≡R</button>
        </div>
      )}

      <div className="card" style={{ padding:0, overflow:"hidden", border: editing ? "2px solid var(--accent)" : "1px solid var(--border)" }}>
        <iframe
          ref={iframeRef}
          srcDoc={html}
          style={{ width:"100%", height:"800px", border:"none", display:"block" }}
          title="Email Preview"
        />
      </div>
    </div>
  )
}
