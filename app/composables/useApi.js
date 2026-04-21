const API_BASE_URL = 'https://dev.api.welltechelectronics.com'
const APP_TENANT = 'f8489cfd-1205-47ac-bad3-8e0a501be570'

function buildRequestHeaders(authToken = null) {
  const headers = {
    'App-Tenant': APP_TENANT
  }

  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }

  return headers
}

async function refreshSession(auth) {
  if (!auth.refreshToken) return null

  const response = await $fetch(`${API_BASE_URL}/auth-microservice/refresh-token`, {
    method: 'POST',
    headers: buildRequestHeaders(),
    body: { refreshToken: auth.refreshToken }
  })

  const data = response.data || response

  if (data?.access_token) {
    auth.updateTokens({
      access_token: data.access_token,
      id_token: data.id_token || null,
      refresh_token: data.refresh_token || auth.refreshToken
    })
  }

  return data
}

export const useApi = () => {
  const auth = useAuthStore()

  return $fetch.create({
    baseURL: API_BASE_URL,

    async onRequest({ options }) {
      const headers = buildRequestHeaders(auth.accessToken)
      options.headers = {
        ...(options.headers || {}),
        ...headers
      }
    },

    async onResponseError({ response, options }) {
      if (response.status !== 401 || !auth.refreshToken) {
        return
      }

      try {
        const data = await refreshSession(auth)

        if (!data?.access_token) {
          auth.logout()
          return
        }

        options.headers = {
          ...(options.headers || {}),
          ...buildRequestHeaders(data.access_token)
        }

        return $fetch(response.url, options)
      } catch {
        auth.logout()
      }
    }
  })
}
