import { useAuthStore } from '~/stores/auth'
// Importamos la lista de rutas y la función de redirección
import { APP_NAV_ITEMS, getDefaultRouteForPermissions } from '~/utils/permissions'

export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()

  // 1. Si intentas entrar a cualquier página (que no sea login) y NO estás logueado
  if (to.path !== '/login' && !auth.accessToken) {
    return navigateTo('/login')
  }

  // 2. Si ya estás logueado e intentas ir al login, te mando al inicio
  if (to.path === '/login' && auth.accessToken) {
    return navigateTo('/')
  }

  // 3. CONTROL DE PERMISOS (Solo si ya estás logueado)
  if (auth.accessToken) {
    // Buscamos si la ruta a la que va el usuario está en nuestra lista de navegación
    const menuItem = APP_NAV_ITEMS.find(item => item.to === to.path)

    // Si la ruta requiere un permiso específico...
    if (menuItem && menuItem.permission) {
      const hasPermission = auth.permissions.includes(menuItem.permission)

      // ...y el usuario NO lo tiene
      if (!hasPermission) {
        console.warn(`Acceso denegado a ${to.path}. Redirigiendo...`)
        
        // Calculamos cuál es la mejor página para este usuario según lo que SÍ puede ver
        const safeRoute = getDefaultRouteForPermissions(auth.permissions)
        return navigateTo(safeRoute)
      }
    }
  }
})