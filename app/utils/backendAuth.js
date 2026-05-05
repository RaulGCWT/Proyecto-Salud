import { useAuthStore } from '~/stores/auth'

export function getBackendToken(auth = null) {
  const authStore = auth || useAuthStore()
  return String(authStore.idToken || authStore.accessToken || '').trim()
}

export function buildBackendAuthHeaders(auth = null, headers = {}) {
  const token = getBackendToken(auth)

  return {
    ...(headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
}

export function buildBackendFetchOptions(auth = null, options = {}) {
  return {
    ...(options || {}),
    headers: buildBackendAuthHeaders(auth, options.headers || {})
  }
}
