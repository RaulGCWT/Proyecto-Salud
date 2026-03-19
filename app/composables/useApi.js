export const useApi = () => {
  const auth = useAuthStore()

  return $fetch.create({
    baseURL: 'https://dev.api.welltechelectronics.com',

    async onRequest({ options }) {
      options.headers = options.headers || {}
      options.headers['App-Tenant'] = 'f8489cfd-1205-47ac-bad3-8e0a501be570'
      
      if (auth.accessToken) {
        options.headers['Authorization'] = `Bearer ${auth.accessToken}`
      }
    },

    async onResponseError({ response, options }) {
      // SI LA API DA ERROR 401 (Token caducado)
      if (response.status === 401 && auth.refreshToken) {
        try {
          // Intentamos el refresco
          const data = await $fetch(`${this.baseURL}/auth-microservice/refresh-token`, {
            method: 'POST',
            headers: { 'App-Tenant': 'f8489cfd-1205-47ac-bad3-8e0a501be570' },
            body: { refreshToken: auth.refreshToken }
          })

          // Guardamos los nuevos tokens (esto actualiza las cookies automáticamente)
          auth.updateTokens(data)

          // Reintentamos la petición original con el nuevo token
          options.headers['Authorization'] = `Bearer ${data.access_token}`
          return $fetch(response.url, options)

        } catch (err) {
          // Si el refresh también falla, limpiamos y al login
          auth.logout()
        }
      }
    }
  })
}