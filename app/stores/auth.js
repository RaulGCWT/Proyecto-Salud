import { defineStore } from 'pinia'
import { buildAccessContext } from '~/utils/permissions'
import {
  getTokenCookieConfig,
  getRefreshTokenCookieConfig,
  resolveAuthStateFromIdToken
} from '~/utils/authTokens'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const accessToken = useCookie('access_token').value || null
    const idToken = useCookie('id_token').value || null
    const refreshToken = useCookie('refresh_token').value || null
    const initialAuthState = resolveAuthStateFromIdToken(idToken)

    return {
      accessToken,
      idToken,
      refreshToken,
      user: initialAuthState.user,
      permissions: initialAuthState.permissions,
      isAuthenticated: !!accessToken
    }
  },

  actions: {
    async login(username, password) {
      try {
        const response = await $fetch('https://dev.api.welltechelectronics.com/auth-microservice/login', {
          method: 'POST',
          headers: { 'App-Tenant': 'f8489cfd-1205-47ac-bad3-8e0a501be570' },
          body: { username, password }
        })

        const data = response.data || response

        if (!data.access_token) {
          throw new Error('No se recibio el token de acceso')
        }

        if (!data.id_token) {
          throw new Error('No se recibio el token de identidad')
        }

        const authState = resolveAuthStateFromIdToken(data.id_token)

        if (!authState.user) {
          throw new Error('No se pudo construir la sesion de usuario')
        }

        this.accessToken = data.access_token
        this.idToken = data.id_token
        this.refreshToken = data.refresh_token || null
        this.user = authState.user
        this.permissions = authState.permissions
        this.isAuthenticated = true

        useCookie('access_token', getTokenCookieConfig(data.access_token)).value = data.access_token
        useCookie('id_token', getTokenCookieConfig(data.id_token)).value = data.id_token

        if (data.refresh_token) {
          useCookie('refresh_token', getRefreshTokenCookieConfig()).value = data.refresh_token
        }
      } catch (error) {
        console.error('Login Error:', error)
        throw error
      }
    },

    logout() {
      this.accessToken = null
      this.idToken = null
      this.refreshToken = null
      this.user = null
      this.permissions = []
      this.isAuthenticated = false

      useCookie('access_token').value = null
      useCookie('id_token').value = null
      useCookie('refresh_token').value = null

      navigateTo('/login')
    },

    getAccessContext() {
      return buildAccessContext(this.user || {})
    }
  }
})
