import client from './client'

// ============================================================
// AUTH
// ============================================================
export const authApi = {
  login: (identifier, password, keepSignedIn = true) =>
    client.post('/api/auth/login', { identifier, password, keep_signed_in: keepSignedIn }),

  sendOtp: (identifier) => client.post('/api/auth/send-otp', { identifier }),

  verifyOtp: (identifier, otp_code) => client.post('/api/auth/verify-otp', { identifier, otp_code }),

  registerCompany: (payload) => client.post('/api/auth/register-company', payload),

  me: () => client.get('/api/auth/me'),
}

// ============================================================
// COMPANY
// ============================================================
export const companyApi = {
  getProfile: () => client.get('/api/company/profile'),
  updateProfile: (payload) => client.put('/api/company/profile', payload),
  getSnapshot: () => client.get('/api/company/snapshot'),
}

// ============================================================
// BRANCHES
// ============================================================
export const branchesApi = {
  list: (params = {}) => client.get('/api/branches', { params }),
  stats: () => client.get('/api/branches/stats'),
  create: (payload) => client.post('/api/branches', payload),
  get: (id) => client.get(`/api/branches/${id}`),
  update: (id, payload) => client.put(`/api/branches/${id}`, payload),
  remove: (id) => client.delete(`/api/branches/${id}`),
}

// ============================================================
// USERS
// ============================================================
export const usersApi = {
  list: (params = {}) => client.get('/api/users', { params }),
  stats: () => client.get('/api/users/stats'),
  invite: (payload) => client.post('/api/users/invite', payload),
  get: (id) => client.get(`/api/users/${id}`),
  update: (id, payload) => client.put(`/api/users/${id}`, payload),
  remove: (id) => client.delete(`/api/users/${id}`),
}

// ============================================================
// ROLES
// ============================================================
export const rolesApi = {
  list: () => client.get('/api/roles'),
  create: (payload) => client.post('/api/roles', payload),
  get: (id) => client.get(`/api/roles/${id}`),
  update: (id, payload) => client.put(`/api/roles/${id}`, payload),
  updatePermissions: (id, permissions) => client.put(`/api/roles/${id}/permissions`, { permissions }),
  remove: (id) => client.delete(`/api/roles/${id}`),
  modules: () => client.get('/api/roles/meta/modules'),
}

// ============================================================
// DASHBOARD
// ============================================================
export const dashboardApi = {
  summary: () => client.get('/api/dashboard/summary'),
  profitLoss: () => client.get('/api/dashboard/profit-loss'),
  production: () => client.get('/api/dashboard/production'),
  attendance: () => client.get('/api/dashboard/attendance'),
  customerFollowup: () => client.get('/api/dashboard/customer-followup'),
}

// ============================================================
// AI ASSISTANT
// ============================================================
export const aiApi = {
  channels: () => client.get('/api/ai/channels'),
  latestConversation: () => client.get('/api/ai/conversations/latest'),
  ask: (message, conversationId = null) =>
    client.post('/api/ai/ask', { message, conversation_id: conversationId }),
}
