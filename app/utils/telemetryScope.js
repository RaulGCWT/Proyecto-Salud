import { buildAccessContext } from '~/utils/accessContext'

export function normalizeScopeValue(value) {
  return String(value || '').trim().toLowerCase()
}

export function normalizeAssignmentType(value) {
  const normalized = normalizeScopeValue(value)
  if (normalized === 'device' || normalized === 'user') return normalized
  return 'none'
}

export function normalizeRuleSide(value) {
  const normalized = normalizeScopeValue(value)
  if (normalized === 'left' || normalized === 'right') return normalized
  return 'all'
}

export function buildTelemetryScope(telemetry = {}) {
  return {
    mac: normalizeScopeValue(telemetry.mac),
    deviceId: normalizeScopeValue(telemetry.deviceId),
    ownerId: normalizeScopeValue(telemetry.ownerId),
    tenantKey: normalizeScopeValue(telemetry.tenantKey),
    residenceId: normalizeScopeValue(telemetry.residenceId),
    area: normalizeScopeValue(telemetry.area),
    residentId: normalizeScopeValue(telemetry.residentId)
  }
}

export function buildDeviceRuleScope(telemetry = {}, device = {}) {
  const telemetryScope = buildTelemetryScope(telemetry)

  return {
    ...telemetryScope,
    ownerId: normalizeScopeValue(device.ownerId || telemetry.ownerId),
    tenantKey: normalizeScopeValue(device.tenantKey || telemetry.tenantKey),
    residenceId: normalizeScopeValue(device.residenceId || telemetry.residenceId),
    area: normalizeScopeValue(device.area || telemetry.area),
    residentId: normalizeScopeValue(device.residentId || telemetry.residentId)
  }
}

export function matchesRuleScope(rule = {}, telemetry = {}, user = {}) {
  const assignmentType = normalizeAssignmentType(rule.assignedToType)
  const assignedToId = normalizeScopeValue(rule.assignedToId)

  // Las reglas sin asignación no deben disparar alertas automáticas sobre ningún dispositivo.
  if (assignmentType === 'none') return false
  if (!assignedToId) return false

  const deviceScope = buildTelemetryScope(telemetry)
  if (assignmentType === 'device') {
    return [deviceScope.mac, deviceScope.deviceId].includes(assignedToId)
  }

  const accessContext = buildAccessContext(user)
  const userTargets = new Set([
    accessContext.tenantKey,
    accessContext.residenceId,
    accessContext.area,
    accessContext.residentId,
    String(user?.email || ''),
    String(user?.id || ''),
    ...accessContext.deviceIds
  ].map(normalizeScopeValue).filter(Boolean))

  return userTargets.has(assignedToId)
}

export function matchesDeviceRuleScope(rule = {}, telemetry = {}, device = {}) {
  const assignmentType = normalizeAssignmentType(rule.assignedToType)
  const assignedToId = normalizeScopeValue(rule.assignedToId)
  const ruleSide = normalizeRuleSide(rule.assignedToSide || rule.side)
  const telemetrySide = normalizeRuleSide(telemetry.side)

  if (assignmentType === 'none') return false
  if (!assignedToId) return false
  if (telemetrySide !== 'all' && ruleSide !== 'all' && ruleSide !== telemetrySide) return false

  const deviceScope = buildDeviceRuleScope(telemetry, device)

  if (assignmentType === 'device') {
    return [deviceScope.mac, deviceScope.deviceId].includes(assignedToId)
  }

  if (assignmentType === 'user') {
    return [
      deviceScope.ownerId,
      deviceScope.tenantKey,
      deviceScope.residenceId,
      deviceScope.area,
      deviceScope.residentId
    ].includes(assignedToId)
  }

  return false
}

export function getLatestTelemetryForMac(records = [], scopeMac = '') {
  const normalizedScopeMac = normalizeScopeValue(scopeMac)
  const scopedRecords = normalizedScopeMac
    ? records.filter(record => normalizeScopeValue(record.mac) === normalizedScopeMac)
    : [...records]

  if (!scopedRecords.length) return null

  const orderedRecords = [...scopedRecords].sort((left, right) => Number(left.ts || 0) - Number(right.ts || 0))
  return orderedRecords.at(-1) || null
}
