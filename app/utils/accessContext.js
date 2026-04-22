import { getPrimaryGroup, normalizeGroupName } from '~/utils/permissions'

const OWNER_SCOPED_ROLES = new Set(['family', 'resident'])
const STAFF_ROLES = new Set(['admin', 'technician', 'clinician', 'members'])
const RULE_ASSIGNMENT_ROLES = new Set(['admin', 'technician', 'members'])

export function buildAccessContext(user = {}) {
  return {
    role: normalizeGroupName(user.role || user.primaryGroup || getPrimaryGroup(user.groups)),
    tenantKey: String(user.tenantKey || ''),
    residenceId: String(user.residenceId || ''),
    area: String(user.area || ''),
    residentId: String(user.residentId || ''),
    deviceIds: Array.isArray(user.deviceIds) ? user.deviceIds : []
  }
}

export function isOwnerScopedRole(role) {
  return OWNER_SCOPED_ROLES.has(normalizeGroupName(role))
}

export function getScopedOwnerId(user = {}) {
  const context = buildAccessContext(user)
  if (!isOwnerScopedRole(context.role)) return ''
  return String(user.email || user.tenantKey || '')
}

export function getPreferredRuleAssignmentRole(user = {}) {
  const groups = Array.isArray(user.groups) ? user.groups : []
  const normalizedGroup = groups
    .map(group => normalizeGroupName(group))
    .find(role => RULE_ASSIGNMENT_ROLES.has(role))

  if (normalizedGroup) return normalizedGroup

  const fallbackRole = normalizeGroupName(user.role || user.primaryGroup)
  return RULE_ASSIGNMENT_ROLES.has(fallbackRole) ? fallbackRole : ''
}

export function canAssignRules(user = {}) {
  return !!getPreferredRuleAssignmentRole(user)
}

export function filterDevicesByAccessContext(devices = [], context = {}) {
  const normalizedContext = buildAccessContext(context)

  if (STAFF_ROLES.has(normalizedContext.role)) {
    return devices
  }

  const allowedDeviceIds = new Set(
    (normalizedContext.deviceIds || [])
      .map(deviceId => String(deviceId || '').trim().toLowerCase())
      .filter(Boolean)
  )

  if (!allowedDeviceIds.size) {
    return []
  }

  return devices.filter((device) => {
    const deviceId = String(device.deviceId || device.id || device.mac || '').trim().toLowerCase()
    return allowedDeviceIds.has(deviceId)
  })
}
