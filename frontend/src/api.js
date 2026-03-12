import axios from "axios"

const BASE = "http://localhost:8000"

export const getRecipients = () => axios.get(`${BASE}/recipients`)
export const getSent       = () => axios.get(`${BASE}/sent`)
export const clearSent     = () => axios.delete(`${BASE}/sent`)
export const sendEmails    = () => axios.post(`${BASE}/send`)

// Multi-job scheduling
export const getJobs       = ()                       => axios.get(`${BASE}/jobs`)
export const getJob        = (job_id)                 => axios.get(`${BASE}/jobs/${job_id}`)
export const postJob       = (run_at, recipients)     => axios.post(`${BASE}/jobs`, { run_at, recipients })
export const deleteJob     = (job_id)                 => axios.delete(`${BASE}/jobs/${job_id}`)
