import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  // Estado: Aquí guardamos los datos "vivos"
    state: () => ({
        user: null,
        token: null,
        isAuthenticated: false,
    }),

  // Acciones: Aquí metemos la lógica de la API
    actions: {
        async login(username, password) {
        try {
            const response = await fetch('https://dev.api.welltechelectronics.com/auth-microservice/login', {
            method: 'POST',
            headers: {
                'App-Tenant': 'f8489cfd-1205-47ac-bad3-8e0a501be570',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
            })

            if (!response.ok) throw new Error('Error en la autenticación')

            const data = await response.json()
            
            // Guardamos los datos en el estado global
            this.token = data.token // Ajusta según el nombre que devuelva tu API
            this.user = data.user
            this.isAuthenticated = true

            return data
        } catch (error) {
            this.isAuthenticated = false
            throw error // Re-lanzamos el error para que la página lo capture
        }
        },

        logout() {
        this.user = null
        this.token = null
        this.isAuthenticated = false
        navigateTo('/login')
        }
    }
})