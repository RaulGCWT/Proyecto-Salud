import { PERMISSIONS } from '~/utils/permissions'

export const APP_NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '📊', permission: PERMISSIONS.DASHBOARD_VIEW },
  { to: '/devices', label: 'Devices', icon: '🛏️', permission: PERMISSIONS.DEVICES_VIEW },
  { to: '/alerts', label: 'Alerts', icon: '⚠️', permission: PERMISSIONS.ALERTS_VIEW },
  { to: '/rules', label: 'Rules', icon: '⚙️', permission: PERMISSIONS.RULES_VIEW },
  { to: '/profile', label: 'My profile', icon: '👤', permission: PERMISSIONS.PROFILE_VIEW },
  { to: '/users', label: 'Admin Panel', icon: '🛠️', permission: PERMISSIONS.USER_ADMINISTRATION }
]

export function getDefaultRouteForPermissions(permissions = []) {
  const permissionSet = new Set(permissions)
  const firstAllowedItem = APP_NAV_ITEMS.find(item => permissionSet.has(item.permission))

  return firstAllowedItem?.to || '/profile'
}
