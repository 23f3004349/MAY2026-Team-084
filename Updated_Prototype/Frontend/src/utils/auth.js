export function getApiBase() {
  return import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";
}

export function getAuthToken() {
  return localStorage.getItem('token')
}

export function getAuthHeader() {
  const token = getAuthToken()
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('token', token)
  } else {
    localStorage.removeItem('token')
  }
}

export function clearAuthToken() {
  localStorage.removeItem('token')
}
