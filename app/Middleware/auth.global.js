export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()

  // Si intentas entrar a una página protegida y NO hay access_token...
  if (to.path !== '/login' && !auth.accessToken) {
    console.log("No hay Access Token, redirigiendo al login...")
    return navigateTo('/login')
  }

  // Si ya estás logueado y vas al login, te mando al inicio
  if (to.path === '/login' && auth.accessToken) {
    return navigateTo('/')
  }
})