import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const idToken = useCookie('id_token').value
    let userData = null

    // Recuperar info del usuario si la cookie ya existe (al refrescar F5)
    if (idToken) {
      try {
        const decoded = jwtDecode(idToken)
        userData = {
          name: decoded.name || 'Usuario',
          email: decoded.email,
          groups: decoded['cognito:groups'] || [],
          tenantKey: decoded['custom:tenant_key'] || ''
        }
      } catch (e) {
        console.error("Error decodificando token inicial", e)
      }
    }

    return {
      accessToken: useCookie('access_token').value || null,
      idToken: idToken || null,
      refreshToken: useCookie('refresh_token').value || null,
      user: userData,
      isAuthenticated: !!useCookie('access_token').value
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

        this.updateTokens(response)
        return response
      } catch (error) {
        throw error
      }
    },

    updateTokens(data) {
      const decodedAccess = jwtDecode(data.access_token)
      const decodedId = jwtDecode(data.id_token)
      
      const currentTime = Math.floor(Date.now() / 1000)
      const secondsRemaining = decodedAccess.exp - currentTime
      const maxAge = secondsRemaining > 0 ? secondsRemaining : 1
      const config = { maxAge, path: '/' }

      // Actualizar estado de Pinia (dispara reactividad)
      this.accessToken = data.access_token
      this.idToken = data.id_token
      if (data.refresh_token) this.refreshToken = data.refresh_token
      this.isAuthenticated = true
      
      // Guardar todos los detalles del usuario
      this.user = { 
        name: decodedId.name || 'Usuario',
        email: decodedId.email,
        groups: decodedId['cognito:groups'] || [],
        tenantKey: decodedId['custom:tenant_key'] || ''
      }

      // Guardar en Cookies
      useCookie('access_token', config).value = data.access_token
      useCookie('id_token', config).value = data.id_token
      if (data.refresh_token) {
        useCookie('refresh_token', { maxAge: 60 * 60 * 24 * 7, path: '/' }).value = data.refresh_token
      }
    },

    logout() {
      this.accessToken = null
      this.idToken = null
      this.refreshToken = null
      this.user = null
      this.isAuthenticated = false
      
      useCookie('access_token').value = null
      useCookie('id_token').value = null
      useCookie('refresh_token').value = null
      
      navigateTo('/login')
    }
  }
})