const rawBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API_BASE = rawBase.replace(/\/$/, '').replace(/\/api$/, '') + '/api'

function getToken() {
  return localStorage.getItem('auth_token')
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }))
    const detail = error.detail
    const message = Array.isArray(detail) ? detail.map((d) => d.msg || d).join(', ') : (detail || `HTTP ${res.status}`)
    throw new Error(message)
  }

  if (res.status === 204) return null
  return res.json()
}

export const api = {
  login: (email, password) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),

  register: (data) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getCurrentMember: () => request('/auth/me'),

  createTeam: (teamName) => request('/team/create', {
    method: 'POST',
    body: JSON.stringify({ team_name: teamName }),
  }),

  joinTeam: (joinCode) => request('/team/join', {
    method: 'POST',
    body: JSON.stringify({ join_code: joinCode }),
  }),

  getMyTeam: () => request('/team/me'),

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

  getMembers: () => request('/members'),
  getMember: (id) => request(`/members/${id}`),
  recomputeRisk: (id) => request(`/members/${id}/recompute-risk`, { method: 'POST' }),

  getReassignments: (memberId) => request(`/reassignments${memberId ? `?member_id=${memberId}` : ''}`),
  resolveReassignment: (id, status) => request(`/reassignments/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ status }),
  }),

  generateSummary: (data) => request('/summary', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  predictRisk: (signals) => request('/predict', {
    method: 'POST',
    body: JSON.stringify(signals),
  }),
}
