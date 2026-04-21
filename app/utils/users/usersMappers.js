const DEFAULT_STAFF_ROLE = 'Call Center Admin'
const DEFAULT_STAFF_AREA = 'Floor 1'
const DEFAULT_RESIDENT_STATUS = 'Pending Setup'
const DEFAULT_FAMILY_STATE = 'Pending'
const DEFAULT_ACTIVE_STATE = 'Active'

export function normalizeText(value, fallback = '') {
  const normalized = String(value ?? '').trim()
  return normalized || fallback
}

export function sameId(left, right) {
  return String(left ?? '') === String(right ?? '')
}

export function createEmptyStaffForm() {
  return {
    id: null,
    name: '',
    email: '',
    role: DEFAULT_STAFF_ROLE,
    area: DEFAULT_STAFF_AREA
  }
}

export function createEmptyResidentForm() {
  return {
    id: null,
    name: '',
    deviceId: '',
    status: DEFAULT_RESIDENT_STATUS,
    notes: ''
  }
}

export function createEmptyFamilyForm() {
  return {
    id: null,
    residentId: '',
    name: '',
    email: '',
    relationship: '',
    state: DEFAULT_FAMILY_STATE,
    patientName: 'Unassigned',
    deviceId: ''
  }
}

export function createEmptyFamilyUserForm() {
  return {
    id: null,
    residentId: '',
    name: '',
    email: '',
    relationship: '',
    state: DEFAULT_ACTIVE_STATE,
    patientName: 'Unassigned',
    deviceId: '',
    deviceIdOverride: ''
  }
}

export function mapStaffMember(item = {}, index = 0) {
  return {
    id: item.id ?? index + 1,
    name: normalizeText(item.name, 'Unknown user'),
    email: normalizeText(item.email),
    role: normalizeText(item.role, DEFAULT_STAFF_ROLE),
    area: normalizeText(item.area, DEFAULT_STAFF_AREA)
  }
}

export function mapResident(item = {}, index = 0) {
  return {
    id: item.id ?? index + 1,
    name: normalizeText(item.name, 'Unknown resident'),
    deviceId: normalizeText(item.deviceId),
    status: normalizeText(item.status, DEFAULT_RESIDENT_STATUS),
    notes: normalizeText(item.notes)
  }
}

export function mapDevice(item = {}, index = 0) {
  const deviceId = normalizeText(item.id || item.deviceId)

  return {
    id: item.id ?? index + 1,
    patientName: normalizeText(item.name, `Bed ${String(deviceId).slice(-5) || index + 1}`),
    deviceId,
    status: normalizeText(item.type, 'Registered')
  }
}

export function mapFamilyAccount(item = {}, residents = [], index = 0) {
  const linkedResident = residents.find(resident =>
    sameId(resident.id, item.residentId) || resident.name === item.patientName
  )

  return {
    id: item.id ?? index + 1,
    residentId: item.residentId || linkedResident?.id || null,
    name: normalizeText(item.name, 'Unknown user'),
    email: normalizeText(item.email),
    patientName: normalizeText(linkedResident?.name || item.patientName, 'Unassigned'),
    deviceId: normalizeText(item.deviceIdOverride || linkedResident?.deviceId || item.deviceId),
    relationship: normalizeText(item.relationship, 'Family'),
    state: normalizeText(item.state, DEFAULT_ACTIVE_STATE),
    deviceIdOverride: normalizeText(item.deviceIdOverride)
  }
}

export function mapInvitation(item = {}, index = 0) {
  const state = String(item.state || 'PENDING').toUpperCase()

  return {
    id: item.id ?? index + 1,
    email: normalizeText(item.email),
    name: normalizeText(item.name),
    patientName: normalizeText(item.patientName, 'Unassigned'),
    relationship: normalizeText(item.relationship),
    residentId: item.residentId || null,
    deviceId: normalizeText(item.deviceId),
    state,
    createdAt: item.createdAt || '',
    expiresAt: item.expiresAt || '',
    acceptedAt: item.acceptedAt || null,
    cancelledAt: item.cancelledAt || null,
    acceptUrl: normalizeText(item.acceptUrl),
    stateLabel: state,
    stateClass: state === 'ACCEPTED' ? 'ok' : state === 'EXPIRED' || state === 'CANCELLED' ? 'danger' : 'warn'
  }
}

export function buildStaffPayload(form = {}) {
  return {
    id: form.id ?? null,
    name: normalizeText(form.name),
    email: normalizeText(form.email),
    role: normalizeText(form.role, DEFAULT_STAFF_ROLE),
    area: normalizeText(form.area, DEFAULT_STAFF_AREA)
  }
}

export function buildResidentPayload(form = {}) {
  return {
    id: form.id ?? null,
    name: normalizeText(form.name),
    deviceId: normalizeText(form.deviceId),
    status: normalizeText(form.status, DEFAULT_RESIDENT_STATUS),
    notes: normalizeText(form.notes)
  }
}

export function buildFamilyInvitePayload(form = {}, resident = null) {
  return {
    id: form.id ?? null,
    residentId: resident?.id || form.residentId || null,
    name: normalizeText(form.name),
    email: normalizeText(form.email),
    relationship: normalizeText(form.relationship, 'Family'),
    state: DEFAULT_FAMILY_STATE,
    patientName: normalizeText(resident?.name || form.patientName, 'Unassigned'),
    deviceId: normalizeText(resident?.deviceId || form.deviceId)
  }
}

export function buildFamilyUserPayload(form = {}, resident = null) {
  return {
    id: form.id ?? null,
    residentId: resident?.id || form.residentId || null,
    name: normalizeText(form.name),
    email: normalizeText(form.email),
    relationship: normalizeText(form.relationship, 'Family'),
    state: normalizeText(form.state, DEFAULT_ACTIVE_STATE),
    patientName: normalizeText(resident?.name || form.patientName, 'Unassigned'),
    deviceId: normalizeText(resident?.deviceId || form.deviceId),
    deviceIdOverride: normalizeText(form.deviceIdOverride)
  }
}
