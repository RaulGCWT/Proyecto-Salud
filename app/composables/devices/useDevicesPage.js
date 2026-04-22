import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { io } from 'socket.io-client'
import { useAuthStore } from '~/stores/auth'
import { PERMISSIONS } from '~/utils/permissions'
import { filterDevicesByAccessContext } from '~/utils/accessContext'

const DEVICES_API_BASE = 'http://localhost:3001/MonitoringDevices'
const SOCKET_URL = 'http://localhost:5000'
const INVENTORY_REFRESH_INTERVAL = 5000
const CONNECTION_TIMEOUT_MS = 4000
const DEFAULT_DEVICE_TYPE = 'Standard'
const ALLOWED_DEVICE_TYPES = new Set(['Critical Care', 'Standard'])

export function useDevicesPage() {
  const auth = useAuthStore()
  const beds = ref([])
  const filters = ref({
    search: '',
    status: 'all',
    type: 'all',
    presence: 'all'
  })
  const lastSeen = ref({})
  const lastInventorySync = ref('Never')
  const heartbeatTick = ref(0)
  const isEditing = ref(false)
  const editingBed = ref(null)
  const editForm = ref({
    name: '',
    type: DEFAULT_DEVICE_TYPE,
    ownerId: ''
  })
  const socketClient = ref(null)
  const inventoryIntervalId = ref(null)
  const connectionIntervalId = ref(null)

  const accessContext = computed(() => auth.getAccessContext())
  const canEditDevices = computed(() => auth.permissions.includes(PERMISSIONS.DEVICES_EDIT))
  const accessibleBeds = computed(() => filterDevicesByAccessContext(beds.value, accessContext.value))

  const ownerOptions = computed(() => {
    const optionMap = new Map()

    const registerOption = (value, label = value) => {
      const normalizedValue = String(value || '').trim()
      const normalizedLabel = String(label || normalizedValue).trim()
      if (!normalizedValue) return
      if (!optionMap.has(normalizedValue)) {
        optionMap.set(normalizedValue, { value: normalizedValue, label: normalizedLabel })
      }
    }

    registerOption(auth.user?.email, auth.user?.email)

    accessibleBeds.value.forEach((bed) => {
      registerOption(bed.ownerId, bed.ownerId)
    })

    return [
      { value: '', label: 'Unassigned' },
      ...Array.from(optionMap.values()).sort((left, right) => left.label.localeCompare(right.label))
    ]
  })

  const deviceStats = computed(() => {
    const connected = accessibleBeds.value.filter(device => device.isOnline).length
    const offline = Math.max(accessibleBeds.value.length - connected, 0)

    return {
      total: accessibleBeds.value.length,
      online: connected,
      offline
    }
  })

  const devicesHeaders = computed(() => ({
    ...(auth.user?.role ? { 'X-Role': auth.user.role } : {}),
    ...(auth.user?.residenceId ? { 'X-Residence-Id': auth.user.residenceId } : {}),
    ...(auth.user?.area ? { 'X-Area': auth.user.area } : {}),
    ...(auth.user?.residentId ? { 'X-Resident-Id': auth.user.residentId } : {}),
    ...(Array.isArray(auth.user?.deviceIds) && auth.user.deviceIds.length ? { 'X-Device-Ids': auth.user.deviceIds.join(',') } : {}),
    ...(auth.user?.email ? { 'X-Owner-Id': auth.user.email } : {})
  }))

  const normalizeMac = (value) => String(value || '').trim().toLowerCase()

  const getSessionCount = (value) => {
    const parsedValue = Number.parseInt(String(value || '0/0').split('/')[0], 10)
    return Number.isFinite(parsedValue) ? parsedValue : 0
  }

  const formatConnectionAge = (elapsedMs) => {
    if (!elapsedMs) return 'Never'

    const safeElapsedMs = Math.max(elapsedMs, 0)
    const elapsedSeconds = Math.floor(safeElapsedMs / 1000)
    const elapsedMinutes = Math.floor(elapsedSeconds / 60)
    const remainingSeconds = elapsedSeconds % 60

    if (elapsedMinutes === 0) {
      return `${remainingSeconds}s`
    }

    if (elapsedMinutes < 60) {
      return `${elapsedMinutes}m ${remainingSeconds}s`
    }

    const elapsedHours = Math.floor(elapsedMinutes / 60)
    const remainingMinutes = elapsedMinutes % 60
    return `${elapsedHours}h ${remainingMinutes}m`
  }

  const getSignalFreshness = (elapsedMs, isOnline) => {
    if (!elapsedMs) return 'No signal'
    if (!isOnline) return 'Silent'

    if (elapsedMs < 15000) return 'Fresh'
    if (elapsedMs < 60000) return 'Warm'
    if (elapsedMs < 180000) return 'Stale'
    return 'Lagging'
  }

  const getFreshnessTone = (freshness) => {
    const normalizedFreshness = String(freshness || '').toLowerCase()
    if (normalizedFreshness === 'fresh') return 'freshness-fresh'
    if (normalizedFreshness === 'warm') return 'freshness-warm'
    if (normalizedFreshness === 'stale') return 'freshness-stale'
    return 'freshness-silent'
  }

  const getTypeTone = (type) => {
    const normalizedType = String(type || '').toLowerCase()
    if (normalizedType.includes('critical')) return 'type-critical'
    if (normalizedType.includes('pump')) return 'type-pump'
    if (normalizedType.includes('vent')) return 'type-life'
    return 'type-standard'
  }

  const getPresenceTone = (presence) => {
    return String(presence || '').toLowerCase() === 'occupied' ? 'presence-occupied' : 'presence-empty'
  }

  const buildSparklineBars = (bed) => {
    const seed = String(bed.mac || bed.name || '')
      .split('')
      .reduce((sum, char) => sum + char.charCodeAt(0), 0)
    const baseLevel = bed.isOnline ? 68 : 26

    return Array.from({ length: 8 }, (_, index) => {
      const variance = ((seed + index * 17) % 20) - 10
      return Math.max(12, Math.min(100, baseLevel + variance))
    })
  }

  const mergeDatabaseDevice = (dbDevice) => {
    const rawMac = String(dbDevice.mac || dbDevice.id || '').trim()
    if (!rawMac) return

    const existingDevice = beds.value.find(device => normalizeMac(device.mac) === normalizeMac(rawMac))
    const nextDevice = {
      mac: rawMac,
      name: dbDevice.name || `Bed-${rawMac.slice(-5)}`,
      type: dbDevice.type || DEFAULT_DEVICE_TYPE,
      ownerId: dbDevice.ownerId || '',
      tenantKey: dbDevice.tenantKey || '',
      residenceId: dbDevice.residenceId || '',
      area: dbDevice.area || '',
      residentId: dbDevice.residentId || ''
    }

    if (existingDevice) {
      Object.assign(existingDevice, nextDevice)
      return
    }

    beds.value.push({
      ...nextDevice,
      isOnline: false,
      presence: 'Empty',
      lastEventDate: 'Never',
      eventCount: '0/0'
    })
  }

  const refreshInventory = async () => {
    try {
      const response = await $fetch(DEVICES_API_BASE, { headers: devicesHeaders.value })
      const inventory = Array.isArray(response) ? response : []

      inventory.forEach(mergeDatabaseDevice)
      lastInventorySync.value = new Date().toLocaleString()
    } catch (error) {
      console.error('Error fetching device inventory:', error)
    }
  }

  const handleSensorUpdate = (data = {}) => {
    const lastReading = data.lastReading || {}
    const incomingMac = normalizeMac(data.mac)
    if (!incomingMac) return

    lastSeen.value[incomingMac] = Date.now()

    const existingDevice = beds.value.find(device => normalizeMac(device.mac) === incomingMac)
    const nowLabel = new Date().toLocaleString()

    if (existingDevice) {
      existingDevice.isOnline = true
      existingDevice.presence = lastReading.isOccupied ? 'Occupied' : 'Empty'
      existingDevice.lastEventDate = nowLabel
      const currentEvents = getSessionCount(existingDevice.eventCount)
      existingDevice.eventCount = `${currentEvents + 1}/${currentEvents + 1}`
      return
    }

    const fallbackId = String(data.deviceId || data.mac || 'unknown').trim()
    beds.value.push({
      mac: data.mac || fallbackId,
      name: `Bed-${fallbackId.slice(-5)}`,
      type: DEFAULT_DEVICE_TYPE,
      isOnline: true,
      presence: lastReading.isOccupied ? 'Occupied' : 'Empty',
      lastEventDate: nowLabel,
      eventCount: '1/1'
    })

    refreshInventory()
  }

  const checkConnections = () => {
    const now = Date.now()

    beds.value.forEach((bed) => {
      if (bed.presence === 'Occupied') {
        bed.isOnline = true
        return
      }

      const bedMac = normalizeMac(bed.mac)
      const lastTimestamp = lastSeen.value[bedMac]
      if (lastTimestamp && (now - lastTimestamp > CONNECTION_TIMEOUT_MS)) {
        bed.isOnline = false
      }
    })
  }

  const editDevice = (bed) => {
    if (!canEditDevices.value) return
    editingBed.value = bed
    editForm.value = {
      name: bed.name || '',
      type: bed.type || DEFAULT_DEVICE_TYPE,
      ownerId: bed.ownerId || ''
    }
    isEditing.value = true
  }

  const closeModal = () => {
    isEditing.value = false
    editingBed.value = null
    editForm.value = {
      name: '',
      type: DEFAULT_DEVICE_TYPE,
      ownerId: ''
    }
  }

  const saveChanges = async (formData = {}) => {
    if (!canEditDevices.value || !editingBed.value) return

    const nextName = String(formData.name || editForm.value.name || '').trim()
    const requestedType = String(formData.type || editForm.value.type || DEFAULT_DEVICE_TYPE).trim()
    const nextType = ALLOWED_DEVICE_TYPES.has(requestedType) ? requestedType : DEFAULT_DEVICE_TYPE
    const nextOwnerId = String(formData.ownerId || editForm.value.ownerId || '').trim()

    if (!nextName) {
      alert('Please enter a valid device name.')
      return
    }

    editForm.value = {
      name: nextName,
      type: nextType
    }

    try {
      await $fetch(`${DEVICES_API_BASE}/${editingBed.value.mac}`, {
        method: 'PUT',
        headers: devicesHeaders.value,
        body: {
          name: nextName,
          type: nextType,
          ownerId: nextOwnerId,
          tenantKey: auth.user?.tenantKey || '',
          residenceId: auth.user?.residenceId || '',
          area: auth.user?.area || '',
          residentId: auth.user?.residentId || ''
        }
      })

      editingBed.value.name = nextName
      editingBed.value.type = nextType
      editingBed.value.ownerId = nextOwnerId
      closeModal()
    } catch (error) {
      console.error('Error saving device changes:', error)
    }
  }

  const resetFilters = () => {
    filters.value = {
      search: '',
      status: 'all',
      type: 'all',
      presence: 'all'
    }
  }

  const filteredBeds = computed(() => {
    const searchTerm = filters.value.search.trim().toLowerCase()

    return accessibleBeds.value.filter((bed) => {
      const bedName = String(bed.name || '').toLowerCase()
      const bedMac = normalizeMac(bed.mac)
      const matchesSearch = !searchTerm || bedName.includes(searchTerm) || bedMac.includes(searchTerm)
      const matchesStatus = filters.value.status === 'all' || (filters.value.status === 'online' ? bed.isOnline : !bed.isOnline)
      const matchesType = filters.value.type === 'all' || bed.type === filters.value.type
      const matchesPresence = filters.value.presence === 'all' || bed.presence === filters.value.presence

      return matchesSearch && matchesStatus && matchesType && matchesPresence
    })
  })

  const healthCards = computed(() => {
    heartbeatTick.value

    return accessibleBeds.value.slice(0, 4).map((bed) => {
      const bedMac = normalizeMac(bed.mac)
      const lastTimestamp = lastSeen.value[bedMac]
      const elapsedMs = lastTimestamp ? Date.now() - lastTimestamp : 0
      const freshness = getSignalFreshness(elapsedMs, bed.isOnline)

      return {
        ...bed,
        sparkline: buildSparklineBars(bed),
        sessionCount: getSessionCount(bed.eventCount).toLocaleString('en-US'),
        connectionAge: formatConnectionAge(elapsedMs),
        lastSeenLabel: elapsedMs ? `Last seen ${formatConnectionAge(elapsedMs)} ago` : 'Last seen never',
        signalFreshness: freshness,
        freshnessTone: getFreshnessTone(freshness)
      }
    })
  })

  onMounted(() => {
    refreshInventory()

    socketClient.value = io(SOCKET_URL)
    socketClient.value.on('sensor_update', handleSensorUpdate)

    inventoryIntervalId.value = window.setInterval(refreshInventory, INVENTORY_REFRESH_INTERVAL)
    connectionIntervalId.value = window.setInterval(() => {
      heartbeatTick.value += 1
      checkConnections()
    }, 1000)
  })

  onBeforeUnmount(() => {
    if (inventoryIntervalId.value) {
      window.clearInterval(inventoryIntervalId.value)
    }
    if (connectionIntervalId.value) {
      window.clearInterval(connectionIntervalId.value)
    }
    if (socketClient.value) {
      socketClient.value.off('sensor_update', handleSensorUpdate)
      socketClient.value.disconnect()
    }
  })

  return {
    filters,
    lastInventorySync,
    canEditDevices,
    accessibleBeds,
    deviceStats,
    filteredBeds,
    healthCards,
    isEditing,
    editingBed,
    editForm,
    refreshInventory,
    checkConnections,
    editDevice,
    closeModal,
    saveChanges,
    resetFilters,
    getTypeTone,
    getPresenceTone,
    ownerOptions
  }
}
