export const PERMISSIONS = {
  DASHBOARD_VIEW: 'dashboard:view',
  DEVICES_VIEW: 'devices:view',
  DEVICES_EDIT: 'devices:edit',
  ALERTS_VIEW: 'alerts:view',
  ALERTS_CLEAR: 'alerts:clear',
  RULES_VIEW: 'rules:view',
  RULES_MANAGE: 'rules:manage',
  PROFILE_VIEW: 'profile:view',
  USER_ADMINISTRATION: 'user:administration',
  USER_CREATE_RECORDS: 'user:create-records'
}

export const GROUP_PERMISSIONS = {
  members: [
    ...Object.values(PERMISSIONS),
    PERMISSIONS.RULES_MANAGE
  ],
  technician: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.DEVICES_VIEW,
    PERMISSIONS.DEVICES_EDIT,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.RULES_VIEW,
    PERMISSIONS.RULES_MANAGE,
    PERMISSIONS.PROFILE_VIEW,
    PERMISSIONS.USER_CREATE_RECORDS
  ],
  clinician: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.PROFILE_VIEW
  ],
  admin: [
    PERMISSIONS.DASHBOARD_VIEW,
    PERMISSIONS.DEVICES_VIEW,
    PERMISSIONS.ALERTS_VIEW,
    PERMISSIONS.RULES_MANAGE,
    PERMISSIONS.PROFILE_VIEW,
    PERMISSIONS.USER_CREATE_RECORDS
  ]
}

export const DEFAULT_AUTHENTICATED_PERMISSIONS = [
  PERMISSIONS.PROFILE_VIEW
]

export function normalizeGroupName(group) {
  return String(group || '').trim().toLowerCase()
}

export function getPrimaryGroup(groups = []) {
  if (!Array.isArray(groups) || !groups.length) return ''
  return normalizeGroupName(groups[0])
}

export function resolvePermissionsFromGroups(groups = []) {
  const resolvedPermissions = new Set(DEFAULT_AUTHENTICATED_PERMISSIONS)

  groups.forEach((group) => {
    const normalizedGroup = normalizeGroupName(group)
    const permissions = GROUP_PERMISSIONS[normalizedGroup] || []

    permissions.forEach((permission) => resolvedPermissions.add(permission))
  })

  return Array.from(resolvedPermissions)
}
