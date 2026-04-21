import { defineStore } from 'pinia'
import { buildAccessContext } from '~/utils/accessContext'
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
    updateTokens(tokens = {}) {
      if (tokens.access_token) {
        this.accessToken = tokens.access_token
        useCookie('access_token', getTokenCookieConfig(tokens.access_token)).value = tokens.access_token
      }

      if (tokens.id_token) {
        this.idToken = tokens.id_token
        useCookie('id_token', getTokenCookieConfig(tokens.id_token)).value = tokens.id_token

        const authState = resolveAuthStateFromIdToken(tokens.id_token)
        this.user = authState.user
        this.permissions = authState.permissions
      }

      if (tokens.refresh_token) {
        this.refreshToken = tokens.refresh_token
        useCookie('refresh_token', getRefreshTokenCookieConfig()).value = tokens.refresh_token
      }

      this.isAuthenticated = !!this.accessToken
    },

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

        this.updateTokens({
          access_token: data.access_token,
          id_token: data.id_token,
          refresh_token: data.refresh_token || null
        })
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
