import { api } from './api'

export const auth = {
  token: null,
  member: null,

  setToken(token) {
    this.token = token
    if (token) localStorage.setItem('auth_token', token)
    else localStorage.removeItem('auth_token')
  },

  setMember(member) {
    this.member = member
    if (member) localStorage.setItem('auth_member', JSON.stringify(member))
    else localStorage.removeItem('auth_member')
  },

  loadFromStorage() {
    this.token = localStorage.getItem('auth_token')
    const memberStr = localStorage.getItem('auth_member')
    if (memberStr) {
      try {
        this.member = JSON.parse(memberStr)
      } catch {
        this.member = null
      }
    }
    return !!(this.token && this.member)
  },

  clear() {
    this.token = null
    this.member = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_member')
  },

  isAuthenticated() {
    return !!this.token && !!this.member
  },

  isManager() {
    return this.member?.role === 'manager'
  },
}

export async function apiLogin(email, password) {
  return api.login(email, password)
}

export async function apiRegister(data) {
  return api.register(data)
}

export async function apiGetMe() {
  return api.getCurrentMember()
}

export async function apiCreateTeam(teamName) {
  return api.createTeam(teamName)
}

export async function apiJoinTeam(joinCode) {
  return api.joinTeam(joinCode)
}

export async function apiGetMyTeam() {
  return api.getMyTeam()
}

export async function apiGetMyTasks() {
  return api.getMyTasks()
}

export async function apiUpdateTaskStatus(taskId, status) {
  return api.updateTaskStatus(taskId, status)
}

export async function apiSubmitSignals(signals) {
  return api.submitSignals(signals)
}

export async function apiGetMyRisk() {
  return api.getMyRisk()
}
