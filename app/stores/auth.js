import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode' // Importación necesaria

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: useCookie('access_token').value || null,
    idToken: useCookie('id_token').value || null,
    refreshToken: useCookie('refresh_token').value || null,
    isAuthenticated: !!useCookie('access_token').value
  }),

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
      // --- LÓGICA CON JWT-DECODE ---
      const decoded = jwtDecode(data.access_token)
      const currentTime = Math.floor(Date.now() / 1000)
      const secondsRemaining = decoded.exp - currentTime

      // Si el token ya expiró por algún motivo, le damos 1s para que se borre
      const maxAge = secondsRemaining > 0 ? secondsRemaining : 1
      
      const config = { maxAge, path: '/' }
      // --- FIN LÓGICA ---

      // Actualizar Pinia
      this.accessToken = data.access_token
      this.idToken = data.id_token
      if (data.refresh_token) this.refreshToken = data.refresh_token
      this.isAuthenticated = true

      // Actualizar Cookies
      useCookie('access_token', config).value = data.access_token
      useCookie('id_token', config).value = data.id_token
      
      // El refresh token suele durar mucho más, lo dejamos en 7 días
      if (data.refresh_token) {
        useCookie('refresh_token', { maxAge: 60 * 60 * 24 * 7, path: '/' }).value = data.refresh_token
      }
      
      console.log(`Sesión sincronizada. Expira en: ${maxAge} segundos.`)
    },

    logout() {
      this.accessToken = null
      this.idToken = null
      this.refreshToken = null
      this.isAuthenticated = false
      
      useCookie('access_token').value = null
      useCookie('id_token').value = null
      useCookie('refresh_token').value = null
      
      navigateTo('/login')
    }
  }
})