import { PERMISSIONS } from '~/utils/permissions'

export const APP_NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: 'dashboard', permission: PERMISSIONS.DASHBOARD_VIEW },
  { to: '/alerts', label: 'Alerts', icon: 'notifications_active', permission: PERMISSIONS.ALERTS_VIEW },
  { to: '/rules', label: 'Rules', icon: 'policy', permission: PERMISSIONS.RULES_VIEW },
  { separator: true, permission: PERMISSIONS.USER_ADMINISTRATION },
  { to: '/admin/devices', label: 'Devices', icon: 'sensors', permission: PERMISSIONS.DEVICES_VIEW },
  { to: '/admin/users', label: 'Admin', icon: 'admin_panel_settings', permission: PERMISSIONS.USER_ADMINISTRATION },
  { to: '/profile', label: 'Profile', icon: 'account_circle', permission: PERMISSIONS.PROFILE_VIEW }
]

export function getDefaultRouteForPermissions(permissions = []) {
  const permissionSet = new Set(permissions)

  const firstAllowedItem = APP_NAV_ITEMS
    .filter(item => item.to && item.permission)
    .find(item => permissionSet.has(item.permission))

  return firstAllowedItem?.to || '/profile'
}
