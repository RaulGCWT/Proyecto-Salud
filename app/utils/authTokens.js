import { jwtDecode } from 'jwt-decode'
import { getPrimaryGroup, resolvePermissionsFromGroups } from '~/utils/permissions'

export function parseDeviceIds(deviceIds) {
  if (!deviceIds) return []

  return String(deviceIds)
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
}

export function getGroupsFromToken(decodedToken = {}) {
  if (!decodedToken || typeof decodedToken !== 'object') return []
  return Array.isArray(decodedToken['cognito:groups']) ? decodedToken['cognito:groups'] : []
}

export function buildUserFromDecodedToken(decodedToken = {}) {
  const groups = getGroupsFromToken(decodedToken)
  const primaryGroup = getPrimaryGroup(groups)

  return {
    name: decodedToken.name || 'Usuario',
    email: decodedToken.email || '',
    groups,
    primaryGroup,
    role: primaryGroup,
    tenantKey: decodedToken['custom:tenant_key'] || '',
    residenceId: decodedToken['custom:residence_id'] || '',
    area: decodedToken['custom:area'] || '',
    residentId: decodedToken['custom:resident_id'] || '',
    deviceIds: parseDeviceIds(decodedToken['custom:device_ids'])
  }
}

export function decodeJwtToken(token) {
  if (!token) return null

  try {
    return jwtDecode(token)
  } catch {
    return null
  }
}

export function resolveAuthStateFromIdToken(idToken) {
  const decodedToken = decodeJwtToken(idToken)

  if (!decodedToken) {
    return {
      user: null,
      permissions: []
    }
  }

  const user = buildUserFromDecodedToken(decodedToken)

  return {
    user,
    permissions: resolvePermissionsFromGroups(user.groups)
  }
}

export function getTokenCookieConfig(token, defaultMaxAge = 60) {
  const decodedToken = decodeJwtToken(token)
  const currentTime = Math.floor(Date.now() / 1000)
  const expirationTime = Number(decodedToken?.exp || 0)
  const secondsRemaining = expirationTime - currentTime

  return {
    maxAge: secondsRemaining > 0 ? secondsRemaining : defaultMaxAge,
    path: '/'
  }
}

export function getRefreshTokenCookieConfig() {
  return {
    maxAge: 60 * 60 * 24 * 7,
    path: '/'
  }
}
