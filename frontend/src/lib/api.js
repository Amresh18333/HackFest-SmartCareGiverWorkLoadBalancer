const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

import { auth } from './auth'

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  // Add auth token if available
  if (auth.token) {
    headers['Authorization'] = `Bearer ${auth.token}`
  }
  
  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  })
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }
  
  return res.json()
}

export const api = {
  // Auth
  login: (email, password) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),
  
  register: (data) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  getCurrentMember: () => request('/auth/me'),
  
  // Team
  createTeam: (teamName) => request('/team/create', {
    method: 'POST',
    body: JSON.stringify({ team_name: teamName }),
  }),
  
  joinTeam: (joinCode) => request('/team/join', {
    method: 'POST',
    body: JSON.stringify({ join_code: joinCode }),
  }),
  
  getMyTeam: () => request('/team/me'),
  
  // Member
  getMyTasks: () => request('/member/tasks'),
  
  updateTaskStatus: (taskId, status) => request(`/member/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
  
  submitSignals: (signals) => request('/member/signals', {
    method: 'POST',
    body: JSON.stringify(signals),
  }),
  
  getMyRisk: () => request('/member/risk'),
  
  // Manager
  getMembers: () => request('/members'),
  getMember: (id) => request(`/members/${id}`),
  recomputeRisk: (id) => request(`/members/${id}/recompute-risk`, { method: 'POST' }),
  
  // Reassignments
  getReassignments: (memberId) => request(`/reassignments${memberId ? `?member_id=${memberId}` : ''}`),
  resolveReassignment: (id, status) => request(`/reassignments/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ status }),
  }),
  
  // Summary
  generateSummary: (data) => request('/summary', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Predict
  predictRisk: (signals) => request('/predict', {
    method: 'POST',
    body: JSON.stringify(signals),
  }),
}