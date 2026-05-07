import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'
import { matchesDeviceRuleScope, normalizeScopeValue } from '~/utils/telemetryScope'

const RESIDENTS_API_BASE = 'http://localhost:5000/residents'
const DEVICE_STREAM_MODE_API_BASE = 'http://localhost:5000/devices'
const REALTIME_DURATION_SECONDS = 30
const HEARTBEAT_TIMEOUT_SECONDS = 45
const TELEMETRY_TIMEOUT_SECONDS = 60

function formatRelativeSeconds(seconds = 0) {
  const safeSeconds = Math.max(0, Math.floor(seconds))
  if (safeSeconds < 60) return `${safeSeconds}s ago`

  const minutes = Math.floor(safeSeconds / 60)
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m ago`
}

function resolveMetricAlert(ruleList = [], metricId = '', currentValue = 0) {
  const normalizedValue = Number(currentValue || 0)

  return ruleList.some((rule) => {
    const parameter = String(rule.parameter || rule.variable || '').trim()
    const threshold = Number(rule.value)
    const condition = String(rule.condition || rule.operator || '').trim()

    if (metricId === 'hr' && !['hr', 'heartRate'].includes(parameter)) return false
    if (metricId === 'hrv' && parameter !== 'hrv') return false
    if (metricId === 'resp' && !['resp', 'respiratoryRate'].includes(parameter)) return false

    if (condition === '>') return normalizedValue > threshold
    if (condition === '<') return normalizedValue < threshold
    if (condition === '=' || condition === '==') return normalizedValue === threshold
    return false
  })
}

export function useDeviceDashboard(route) {
  const auth = useAuthStore()
  const health = useHealthStore()
  const rulesStore = useRulesStore()
  const isLoading = ref(true)
  const isRealtimePending = ref(false)
  const realtimeSecondsLeft = ref(0)
  const realtimeTimerId = ref(null)

  const { data: residentsData } = useFetch(RESIDENTS_API_BASE, {
    server: false,
    headers: buildBackendAuthHeaders(auth),
    default: () => []
  })

  async function syncRouteScope() {
    const routeMac = normalizeScopeValue(route.params.mac)
    if (!routeMac) return

    isLoading.value = true

    try {
      health.setSelectedMac(routeMac)
      await Promise.all([
        rulesStore.fetchRules(),
        health.fetchDeviceInventory(),
        health.fetchAlertHistory()
      ])
      await health.fetchTelemetryHistory(200, routeMac)
    } finally {
      isLoading.value = false
    }
  }

  function clearRealtimeTimer() {
    if (!realtimeTimerId.value) return
    window.clearInterval(realtimeTimerId.value)
    realtimeTimerId.value = null
  }

  function startRealtimeCountdown(durationSeconds = REALTIME_DURATION_SECONDS) {
    clearRealtimeTimer()
    realtimeSecondsLeft.value = Math.max(0, Number(durationSeconds || REALTIME_DURATION_SECONDS))

    realtimeTimerId.value = window.setInterval(() => {
      if (realtimeSecondsLeft.value <= 1) {
        realtimeSecondsLeft.value = 0
        clearRealtimeTimer()
        return
      }

      realtimeSecondsLeft.value -= 1
    }, 1000)
  }

  async function startRealtimeMode() {
    const routeMac = normalizeScopeValue(route.params.mac)
    if (!routeMac || isRealtimePending.value || realtimeSecondsLeft.value > 0) return

    isRealtimePending.value = true

    try {
      const response = await $fetch(`${DEVICE_STREAM_MODE_API_BASE}/${routeMac}/stream-mode`, {
        method: 'POST',
        headers: buildBackendAuthHeaders(auth),
        body: {
          mode: 'realtime',
          durationSeconds: REALTIME_DURATION_SECONDS
        }
      })

      startRealtimeCountdown(response?.durationSeconds || REALTIME_DURATION_SECONDS)
    } catch (error) {
      console.error('Could not activate real time mode:', error)
      alert('Could not activate real time mode for this device.')
    } finally {
      isRealtimePending.value = false
    }
  }

  const currentDeviceRecord = computed(() => {
    const routeMac = normalizeScopeValue(route.params.mac)

    return health.deviceInventory.find((device) => {
      const deviceMac = normalizeScopeValue(device.mac)
      const deviceId = normalizeScopeValue(device.deviceId)
      return deviceMac === routeMac || deviceId === routeMac
    }) || null
  })

  const residents = computed(() => Array.isArray(residentsData.value) ? residentsData.value : [])

  const residentsById = computed(() => {
    const residentMap = new Map()

    for (const resident of residents.value) {
      const residentId = normalizeScopeValue(resident.id || resident.residentId)
      if (!residentId) continue
      residentMap.set(residentId, resident)
    }

    return residentMap
  })

  const currentPatientLabel = computed(() => {
    const currentDevice = currentDeviceRecord.value
    if (!currentDevice) {
      return 'Patient not assigned'
    }

    // Reutilizamos el mismo criterio del overview para no mostrar UUIDs internos en la UI.
    const linkedResident = residentsById.value.get(normalizeScopeValue(currentDevice.residentId))
      || residents.value.find((resident) => {
        const residentDeviceId = normalizeScopeValue(resident.deviceId)
        return residentDeviceId && (
          residentDeviceId === normalizeScopeValue(currentDevice.mac)
          || residentDeviceId === normalizeScopeValue(currentDevice.deviceId)
          || residentDeviceId === normalizeScopeValue(currentDevice.name)
        )
      })

    return linkedResident?.name || currentDevice.ownerId || currentDevice.name || 'Patient not assigned'
  })

  const currentTitle = computed(() => {
    const deviceId = currentDeviceRecord.value?.deviceId || health.currentDeviceId || route.params.mac
    return `${deviceId} · ${currentPatientLabel.value}`
  })

  const scopedRules = computed(() => {
    const routeMac = normalizeScopeValue(route.params.mac)

    return rulesStore.rules.filter(rule => matchesDeviceRuleScope(rule, {
      mac: routeMac,
      deviceId: normalizeScopeValue(currentDeviceRecord.value?.deviceId),
      side: normalizeScopeValue(health.selectedSide)
    }, currentDeviceRecord.value || {}))
  })

  const scopedAlerts = computed(() => {
    const routeMac = normalizeScopeValue(route.params.mac)

    return health.alertHistory
      .filter((alert) => {
        const alertMac = normalizeScopeValue(alert.mac)
        const alertDeviceId = normalizeScopeValue(alert.deviceId)
        return alertMac === routeMac || alertDeviceId === routeMac
      })
      .slice(0, 5)
  })

  const activeAlertsCount = computed(() => {
    return scopedAlerts.value.filter(alert => String(alert.status || '').toUpperCase() !== 'READ').length
  })

  const heartbeatSecondsAgo = computed(() => {
    const heartbeatTs = Number(currentDeviceRecord.value?.lastHeartbeatTs || 0)
    if (!heartbeatTs) return null
    return Math.max(0, Math.floor(Date.now() / 1000) - heartbeatTs)
  })

  const latestTelemetryTimestamp = computed(() => {
    const records = Array.isArray(health.latestReadings) ? health.latestReadings : []
    const lastRecord = records.at(-1)
    return Number(lastRecord?.ts || 0) || 0
  })

  const telemetrySecondsAgo = computed(() => {
    if (!latestTelemetryTimestamp.value) return null
    return Math.max(0, Math.floor(Date.now() / 1000) - latestTelemetryTimestamp.value)
  })

  const connectionLabel = computed(() => {
    const connectionState = normalizeScopeValue(currentDeviceRecord.value?.connectionState)
    if (connectionState !== 'online') return 'Offline'
    if (heartbeatSecondsAgo.value === null || heartbeatSecondsAgo.value > HEARTBEAT_TIMEOUT_SECONDS) {
      return 'Offline'
    }
    return 'Connected'
  })

  const telemetryStateLabel = computed(() => {
    if (telemetrySecondsAgo.value === null) return 'Waiting for telemetry'
    if (telemetrySecondsAgo.value > TELEMETRY_TIMEOUT_SECONDS) return 'Telemetry delayed'
    return 'Telemetry active'
  })

  const isDeviceActivelyStreaming = computed(() => {
    return telemetrySecondsAgo.value !== null && telemetrySecondsAgo.value <= TELEMETRY_TIMEOUT_SECONDS
  })

  const lastHeartbeatLabel = computed(() => {
    if (heartbeatSecondsAgo.value === null) return 'No heartbeat yet'
    return formatRelativeSeconds(heartbeatSecondsAgo.value)
  })

  const lastTelemetryLabel = computed(() => {
    if (telemetrySecondsAgo.value === null) return 'No telemetry yet'
    return formatRelativeSeconds(telemetrySecondsAgo.value)
  })

  const sidePanelRows = computed(() => {
    return [
      {
        key: 'device',
        label: 'Device ID',
        value: health.currentDeviceId,
        tone: 'neutral'
      },
      {
        key: 'patient',
        label: 'Patient',
        value: currentPatientLabel.value,
        tone: 'neutral'
      },
      {
        key: 'connection',
        label: 'Connection',
        value: connectionLabel.value,
        tone: connectionLabel.value === 'Connected' ? 'ok' : 'danger'
      },
      {
        key: 'telemetry',
        label: 'Telemetry',
        value: telemetryStateLabel.value,
        tone: telemetryStateLabel.value === 'Telemetry active'
          ? 'ok'
          : telemetryStateLabel.value === 'Telemetry delayed'
            ? 'warn'
            : 'neutral'
      },
      {
        key: 'heartbeat',
        label: 'Last heartbeat',
        value: lastHeartbeatLabel.value,
        tone: 'neutral'
      },
      {
        key: 'last-telemetry',
        label: 'Last telemetry',
        value: lastTelemetryLabel.value,
        tone: 'neutral'
      },
      {
        key: 'alerts',
        label: 'Active alerts',
        value: String(activeAlertsCount.value),
        tone: activeAlertsCount.value > 0 ? 'danger' : 'ok'
      },
      {
        key: 'rules',
        label: 'Rules loaded',
        value: String(scopedRules.value.length),
        tone: 'neutral'
      }
    ]
  })

  const realtimeButtonLabel = computed(() => {
    if (isRealtimePending.value) return 'Starting...'
    if (realtimeSecondsLeft.value > 0) return `Real time active (${realtimeSecondsLeft.value}s)`
    return 'Start real time'
  })

  const dashboardCards = computed(() => {
    return [
      {
        key: 'hr',
        type: 'hr',
        title: 'Heart rate',
        subtitle: 'Current average',
        mainText: `${health.heartRate || 0} BPM`,
        isAlert: resolveMetricAlert(scopedRules.value, 'hr', health.heartRate)
      },
      {
        key: 'hrv',
        type: 'hrv',
        title: 'HR variability',
        subtitle: 'Current average',
        mainText: `${health.hrv || 0} ms`,
        isAlert: resolveMetricAlert(scopedRules.value, 'hrv', health.hrv)
      },
      {
        key: 'resp',
        type: 'resp',
        title: 'Resp. rate',
        subtitle: 'Current average',
        mainText: `${health.respiratoryRate || 0} RPM`,
        isAlert: resolveMetricAlert(scopedRules.value, 'resp', health.respiratoryRate)
      },
      {
        key: 'presence',
        type: 'presence',
        title: 'Bed status',
        subtitle: 'Current stream state',
        mainText: isDeviceActivelyStreaming.value ? 'In Use' : 'Empty',
        isAlert: false
      }
    ]
  })

  onMounted(syncRouteScope)
  onBeforeUnmount(clearRealtimeTimer)
  watch(() => route.params.mac, syncRouteScope)

  return {
    health,
    isLoading,
    currentDeviceRecord,
    currentPatientLabel,
    currentTitle,
    scopedRules,
    scopedAlerts,
    sidePanelRows,
    dashboardCards,
    isRealtimePending,
    realtimeSecondsLeft,
    realtimeButtonLabel,
    startRealtimeMode
  }
}
