import { PERMISSIONS } from '~/utils/permissions'

export const APP_NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'dashboard', permission: PERMISSIONS.DASHBOARD_VIEW },
  { to: '/devices', label: 'Devices', icon: 'sensors', permission: PERMISSIONS.DEVICES_VIEW },
  { to: '/alerts', label: 'Alerts', icon: 'notifications_active', permission: PERMISSIONS.ALERTS_VIEW },
  { to: '/rules', label: 'Rules', icon: 'policy', permission: PERMISSIONS.RULES_VIEW },
  { to: '/users', label: 'Users', icon: 'groups', permission: PERMISSIONS.USER_ADMINISTRATION },
  { to: '/profile', label: 'Profile', icon: 'account_circle', permission: PERMISSIONS.PROFILE_VIEW }
]

export function getDefaultRouteForPermissions(permissions = []) {
  const permissionSet = new Set(permissions)
  const preferredRoutes = ['/', '/devices', '/alerts', '/rules', '/users', '/profile']

  const firstAllowedItem = preferredRoutes
    .map(route => APP_NAV_ITEMS.find(item => item.to === route && permissionSet.has(item.permission)))
    .find(Boolean)

  return firstAllowedItem?.to || '/profile'
}
