import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import { useState } from "react"
import Recipients from "./pages/Recipients"
import Preview    from "./pages/Preview"
import Schedule   from "./pages/Schedule"
import Jobs       from "./pages/Jobs"
import SentLog    from "./pages/SentLog"
import "./App.css"

export default function App() {
  const [selectedRecipients, setSelectedRecipients] = useState([])

  return (
    <BrowserRouter>
      <nav className="nav">
        <div className="nav-logo">✉ Emailer</div>
        <NavLink to="/">Recipients</NavLink>
        <NavLink to="/preview">Preview</NavLink>
        <NavLink to="/schedule">Run & Schedule</NavLink>
        <NavLink to="/jobs">Jobs</NavLink>
        <NavLink to="/sent">Sent Log</NavLink>
      </nav>
      <div className="main">
        <Routes>
          <Route path="/"         element={<Recipients selected={selectedRecipients} setSelected={setSelectedRecipients} />} />
          <Route path="/preview"  element={<Preview />} />
          <Route path="/schedule" element={<Schedule selected={selectedRecipients} setSelected={setSelectedRecipients} />} />
          <Route path="/jobs"     element={<Jobs />} />
          <Route path="/sent"     element={<SentLog />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
