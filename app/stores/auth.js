import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode'
// 1. Importamos el helper de permisos
import { buildAccessContext, getPrimaryGroup, resolvePermissionsFromGroups } from '~/utils/permissions'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const idToken = useCookie('id_token').value
    let userData = null
    let initialPermissions = []

    // 2. Recuperar info y RECALCULAR permisos al refrescar (F5)
    if (idToken) {
      try {
        const decoded = jwtDecode(idToken)
        const groups = decoded['cognito:groups'] || []
        const primaryGroup = getPrimaryGroup(groups)
        
        userData = {
          name: decoded.name || 'Usuario',
          email: decoded.email,
          groups: groups,
          primaryGroup,
          role: primaryGroup,
          tenantKey: decoded['custom:tenant_key'] || '',
          residenceId: decoded['custom:residence_id'] || '',
          area: decoded['custom:area'] || '',
          residentId: decoded['custom:resident_id'] || '',
          deviceIds: decoded['custom:device_ids']
            ? String(decoded['custom:device_ids']).split(',').map(item => item.trim()).filter(Boolean)
            : []
        }
        
        // Traducimos los grupos guardados en la cookie a permisos reales
        initialPermissions = resolvePermissionsFromGroups(groups)
      } catch (e) {
        console.error("Error decodificando token inicial", e)
      }
    }

    return {
      accessToken: useCookie('access_token').value || null,
      idToken: idToken || null,
      refreshToken: useCookie('refresh_token').value || null,
      user: userData,
      permissions: initialPermissions, // <--- Nuevo estado de permisos
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
        const data = response.data || response 

        if (!data.access_token) {
          console.error("Estructura de data recibida:", data)
          throw new Error("No se recibió el token de acceso")
      }

        const decodedAccess = jwtDecode(data.access_token)
        const decodedId = jwtDecode(data.id_token)
        
        const currentTime = Math.floor(Date.now() / 1000)
        const secondsRemaining = decodedAccess.exp - currentTime
        const maxAge = secondsRemaining > 0 ? secondsRemaining : 1
        const config = { maxAge, path: '/' }

        // Actualizar estado de Pinia
        this.accessToken = data.access_token
        this.idToken = data.id_token
        if (data.refresh_token) this.refreshToken = data.refresh_token
        this.isAuthenticated = true
        
        // 3. Extraer grupos y asignar permisos en el Login
        const groups = decodedId['cognito:groups'] || []
        const primaryGroup = getPrimaryGroup(groups)
        this.user = { 
          name: decodedId.name || 'Usuario',
          email: decodedId.email,
          groups: groups,
          primaryGroup,
          role: primaryGroup,
          tenantKey: decodedId['custom:tenant_key'] || '',
          residenceId: decodedId['custom:residence_id'] || '',
          area: decodedId['custom:area'] || '',
          residentId: decodedId['custom:resident_id'] || '',
          deviceIds: decodedId['custom:device_ids']
            ? String(decodedId['custom:device_ids']).split(',').map(item => item.trim()).filter(Boolean)
            : []
        }
        
        // Convertimos grupos a permisos usando el helper
        this.permissions = resolvePermissionsFromGroups(groups)

        // Guardar en Cookies
        useCookie('access_token', config).value = data.access_token
        useCookie('id_token', config).value = data.id_token
        if (data.refresh_token) {
          useCookie('refresh_token', { maxAge: 60 * 60 * 24 * 7, path: '/' }).value = data.refresh_token
        }
      } catch (error) {
        console.error("Login Error:", error)
        throw error
      }
    },

    logout() {
      // 4. Limpiar permisos al cerrar sesión
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
