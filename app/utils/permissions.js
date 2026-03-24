// Definición de constantes para evitar "strings mágicos" y errores de dedo en el código
export const PERMISSIONS = {
  DASHBOARD_VIEW: 'dashboard:view',
  DEVICES_VIEW: 'devices:view',
  DEVICES_EDIT: 'devices:edit',
  ALERTS_VIEW: 'alerts:view',
  ALERTS_CLEAR: 'alerts:clear',
  RULES_VIEW: 'rules:view',
  RULES_MANAGE: 'rules:manage',
  PROFILE_VIEW: 'profile:view'
}

// Mapeo de qué permisos tiene cada rol/grupo de usuario
export const GROUP_PERMISSIONS = {
  // El admin recibe todos los valores definidos en el objeto PERMISSIONS
  admin: Object.values(PERMISSIONS),
  // El técnico tiene permisos de visualización y edición de dispositivos/reglas
  technician: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.DEVICES_VIEW,
    PERMISSIONS.DEVICES_EDIT,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.RULES_VIEW,
    PERMISSIONS.PROFILE_VIEW
  ],
  // El clínico tiene un acceso más restringido (lectura básica)
  clinician: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.PROFILE_VIEW
  ],
  // Miembros estándar con acceso a dispositivos pero no a edición o reglas
  members: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.DEVICES_VIEW,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.PROFILE_VIEW
  ]
}

// Permisos mínimos que cualquier usuario logueado tiene, independientemente de su grupo
export const DEFAULT_AUTHENTICATED_PERMISSIONS = [
  PERMISSIONS.PROFILE_VIEW
]

// Configuración de la barra de navegación: asocia una ruta con un permiso requerido
export const APP_NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '📊', permission: PERMISSIONS.DASHBOARD_VIEW },
  { to: '/devices', label: 'Devices', icon: '🛏️', permission: PERMISSIONS.DEVICES_VIEW },
  { to: '/alerts', label: 'Alerts', icon: '⚠️', permission: PERMISSIONS.ALERTS_VIEW },
  { to: '/rules', label: 'Rules', icon: '⚙️', permission: PERMISSIONS.RULES_VIEW },
  { to: '/profile', label: 'My profile', icon: '👤', permission: PERMISSIONS.PROFILE_VIEW }
]

/**
 * Limpia el nombre de un grupo para que coincida con las llaves de GROUP_PERMISSIONS
 * @param {string} group - El nombre del grupo (ej: "  Admin ")
 * @returns {string} - El nombre normalizado (ej: "admin")
 */
export function normalizeGroupName(group) {
  // Convierte a string, quita espacios en blanco y pasa a minúsculas
  return String(group || '').trim().toLowerCase()
}

/**
 * Consolida todos los permisos de múltiples grupos en una sola lista sin duplicados
 */
export function resolvePermissionsFromGroups(groups = []) {
  // Crea un Set (colección de valores únicos) inicializado con los permisos base
  const resolvedPermissions = new Set(DEFAULT_AUTHENTICATED_PERMISSIONS)

  // Itera sobre cada grupo asignado al usuario
  groups.forEach((group) => {
    // Normaliza el nombre para evitar fallos por mayúsculas/espacios
    const normalizedGroup = normalizeGroupName(group)
    // Obtiene el array de permisos de ese grupo o un array vacío si no existe
    const permissions = GROUP_PERMISSIONS[normalizedGroup] || []

    // Agrega cada permiso del grupo al Set (el Set ignora automáticamente los repetidos)
    permissions.forEach((permission) => resolvedPermissions.add(permission))
  })
  return Array.from(resolvedPermissions)
}

export function getDefaultRouteForPermissions(permissions = []) {
  // Convertimos los permisos a Set para que la búsqueda (.has) sea mucho más rápida
  const permissionSet = new Set(permissions)
  
  // Busca en la lista de navegación el primer item para el cual el usuario tenga permiso
  const firstAllowedItem = APP_NAV_ITEMS.find(item => permissionSet.has(item.permission))

  // Si encuentra uno, devuelve su ruta ('to'), si no, lo manda a '/profile' por defecto
  return firstAllowedItem?.to || '/profile'
}