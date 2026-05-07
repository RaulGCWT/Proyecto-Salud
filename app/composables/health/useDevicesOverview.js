import { computed, ref } from 'vue'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { useAuthStore } from '~/stores/auth'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'
import { matchesDeviceRuleScope, normalizeScopeValue } from '~/utils/telemetryScope'

const OFFLINE_TIMEOUT_SECONDS = 60
const HEARTBEAT_TIMEOUT_SECONDS = 45
const RESIDENTS_API_BASE = 'http://localhost:5000/residents'

function buildTelemetrySeries(records = [], metricKey = 'heartRate', limit = 10) {
  return [...records]
    .sort((left, right) => Number(left.ts || 0) - Number(right.ts || 0))
    .slice(-Math.max(2, limit))
    .map(record => Number(record[metricKey] || 0))
    .filter(value => Number.isFinite(value) && value > 0)
}

function getSeriesBounds(series = []) {
  const values = series.filter(value => Number.isFinite(value))
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)

  return {
    minimum: Number.isFinite(minimum) ? minimum : 0,
    maximum: Number.isFinite(maximum) ? maximum : 0
  }
}

function buildSparklinePath(series = []) {
  if (!series.length) {
    return ''
  }

  const { minimum, maximum } = getSeriesBounds(series)
  const spread = Math.max(maximum - minimum, 1)

  return series
    .map((value, index) => {
      const x = series.length === 1 ? 0 : (index / (series.length - 1)) * 100
      const y = 24 - (((value - minimum) / spread) * 18)
      return `${index === 0 ? 'M' : 'L'}${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

function formatRelativeSeconds(seconds = 0) {
  const safeSeconds = Math.max(0, Math.floor(seconds))
  if (safeSeconds < 60) return `${safeSeconds}s`

  const minutes = Math.floor(safeSeconds / 60)
  if (minutes < 60) return `${minutes}m`

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m`
}

function extractTriggeredMetric(rule = {}, reading = {}) {
  const parameter = String(rule.parameter || rule.variable || '').trim()
  if (parameter === 'hr' || parameter === 'heartRate') return Number(reading.heartRate || 0)
  if (parameter === 'hrv') return Number(reading.hrv || 0)
  if (parameter === 'resp' || parameter === 'respiratoryRate') return Number(reading.respiratoryRate || 0)
  return 0
}

function isRuleTriggered(rule = {}, reading = {}) {
  const threshold = Number(rule.value)
  const metricValue = extractTriggeredMetric(rule, reading)
  const condition = String(rule.condition || rule.operator || '').trim()

  if (!Number.isFinite(metricValue) || !Number.isFinite(threshold)) return false
  if (condition === '>') return metricValue > threshold
  if (condition === '<') return metricValue < threshold
  if (condition === '=' || condition === '==') return metricValue === threshold
  return false
}

function buildDeviceAliases(device = {}) {
  return new Set([
    normalizeScopeValue(device.mac),
    normalizeScopeValue(device.deviceId),
    normalizeScopeValue(device.id)
  ].filter(Boolean))
}

function findExistingDeviceKey(deviceMap, aliases = new Set()) {
  for (const [key, entry] of deviceMap.entries()) {
    const entryAliases = buildDeviceAliases(entry)

    for (const alias of aliases) {
      if (entryAliases.has(alias)) {
        return key
      }
    }
  }

  return ''
}

export function useDevicesOverview() {
  const health = useHealthStore()
  const rulesStore = useRulesStore()
  const auth = useAuthStore()
  const searchQuery = ref('')
  const backendHeaders = computed(() => buildBackendAuthHeaders(auth))
  const { data: residentsData } = useFetch(RESIDENTS_API_BASE, {
    server: false,
    headers: backendHeaders.value,
    default: () => []
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

  const deviceCards = computed(() => {
    const deviceMap = new Map()
    const inventoryDevices = Array.isArray(health.deviceInventory) ? health.deviceInventory : []

    if (!inventoryDevices.length) {
      return []
    }

    for (const device of inventoryDevices) {
      const aliases = buildDeviceAliases(device)
      const primaryKey = findExistingDeviceKey(deviceMap, aliases) || normalizeScopeValue(device.mac || device.deviceId)
      if (!primaryKey) continue

      deviceMap.set(primaryKey, {
        ...device,
        mac: normalizeScopeValue(device.mac),
        deviceId: String(device.deviceId || device.name || device.mac || '').trim()
      })
    }

    return Array.from(deviceMap.values()).map((device) => {
      const deviceAliases = buildDeviceAliases(device)
      const primaryAlias = normalizeScopeValue(device.mac || device.deviceId)
      const residentId = normalizeScopeValue(device.residentId)
      const linkedResident = residentsById.value.get(residentId) || residents.value.find((resident) => {
        const residentDeviceId = normalizeScopeValue(resident.deviceId)
        return residentDeviceId && (
          residentDeviceId === normalizeScopeValue(device.mac) ||
          residentDeviceId === normalizeScopeValue(device.deviceId) ||
          residentDeviceId === normalizeScopeValue(device.name)
        )
      }) || null
      const records = health.telemetryRecords
        .filter(record => {
          const recordAliases = buildDeviceAliases(record)

          for (const alias of recordAliases) {
            if (deviceAliases.has(alias)) {
              return true
            }
          }

          return false
        })
        .sort((left, right) => Number(left.ts || 0) - Number(right.ts || 0))

      const latestRecord = records.at(-1) || null
      const latestTimestamp = Number(latestRecord?.ts || 0)
      const latestBatch = latestTimestamp
        ? records.filter(record => Number(record.ts || 0) === latestTimestamp)
        : []
      const scopedAlerts = health.alertHistory.filter((alert) => {
        const alertAliases = buildDeviceAliases(alert)

        for (const alias of alertAliases) {
          if (deviceAliases.has(alias)) {
            return true
          }
        }

        return false
      })
      const openAlerts = scopedAlerts.filter(alert => String(alert.status || '').toUpperCase() !== 'READ')
      const activeRules = rulesStore.rules.filter(rule => matchesDeviceRuleScope(rule, {
        mac: normalizeScopeValue(device.mac),
        deviceId: normalizeScopeValue(device.deviceId),
        side: 'all'
      }, device))
      const hasRuleWarning = latestBatch.some(reading => activeRules.some(rule => isRuleTriggered(rule, reading)))
      const latestSecondsAgo = latestTimestamp > 0 ? Math.max(0, Math.floor(Date.now() / 1000) - latestTimestamp) : null
      const latestHeartbeatTs = Number(device.lastHeartbeatTs || 0)
      const heartbeatSecondsAgo = latestHeartbeatTs > 0 ? Math.max(0, Math.floor(Date.now() / 1000) - latestHeartbeatTs) : null
      const isConnected = normalizeScopeValue(device.connectionState) === 'online'
        && heartbeatSecondsAgo !== null
        && heartbeatSecondsAgo <= HEARTBEAT_TIMEOUT_SECONDS
      const isOnline = latestSecondsAgo !== null && latestSecondsAgo <= OFFLINE_TIMEOUT_SECONDS
      const averageMetric = (metricKey) => {
        const values = latestBatch
          .map(item => Number(item[metricKey] || 0))
          .filter(value => Number.isFinite(value) && value > 0)

        if (!values.length) return 0
        return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length)
      }
      const heartSeries = buildTelemetrySeries(records, 'heartRate')
      const respiratorySeries = buildTelemetrySeries(records, 'respiratoryRate')
      const hrvSeries = buildTelemetrySeries(records, 'hrv')
      const status = !isConnected
        ? 'offline'
        : !isOnline
          ? 'connected'
          : openAlerts.length
          ? 'urgent'
          : hasRuleWarning
            ? 'attention'
            : 'stable'
      const lastSeenLabel = !isConnected
        ? 'Disconnected'
        : latestSecondsAgo === null
          ? 'Connected · waiting telemetry'
          : `${formatRelativeSeconds(latestSecondsAgo)} ago`

      return {
        ...device,
        mac: normalizeScopeValue(device.mac || primaryAlias),
        deviceId: String(device.deviceId || device.name || primaryAlias).trim(),
        deviceName: String(device.name || device.deviceId || primaryAlias).trim(),
        residentName: String(linkedResident?.name || 'Resident not assigned').trim(),
        heartRate: averageMetric('heartRate'),
        respiratoryRate: averageMetric('respiratoryRate'),
        hrv: averageMetric('hrv'),
        isOccupied: latestBatch.some(item => Boolean(item.isOccupied)),
        openAlertsCount: openAlerts.length,
        latestAlertMessage: openAlerts[0]?.message || scopedAlerts[0]?.message || '',
        latestAlertStatus: openAlerts[0]?.status || scopedAlerts[0]?.status || '',
        status,
        isConnected,
        isOnline,
        lastSeenLabel,
        sparklinePaths: {
          heartRate: buildSparklinePath(heartSeries),
          respiratoryRate: buildSparklinePath(respiratorySeries),
          hrv: buildSparklinePath(hrvSeries)
        },
        telemetryCount: records.length
      }
    })
  })

  const visibleDeviceCards = computed(() => {
    const normalizedSearch = String(searchQuery.value || '').trim().toLowerCase()

    const filteredCards = deviceCards.value.filter((card) => {
      return !normalizedSearch || [
        card.mac,
        card.deviceName,
        card.residentName
      ].some(value => String(value || '').toLowerCase().includes(normalizedSearch))
    })

    return [...filteredCards].sort((left, right) => {
      return String(left.deviceId || left.deviceName).localeCompare(String(right.deviceId || right.deviceName), undefined, {
        numeric: true,
        sensitivity: 'base'
      })
    })
  })

  const overviewStats = computed(() => {
    const cards = deviceCards.value
    const onlineCards = cards.filter(card => card.isConnected)
    const stableCards = cards.filter(card => card.status === 'stable')
    const attentionCards = cards.filter(card => card.status === 'attention')
    const urgentCards = cards.filter(card => card.status === 'urgent')

    return [
      {
        key: 'global',
        label: 'Global Status',
        value: onlineCards.length,
        note: 'Active Monitoring',
        icon: 'sensors',
        tone: 'overview-stat--global'
      },
      {
        key: 'stable',
        label: 'Stable',
        value: stableCards.length,
        note: 'Normal Status',
        icon: 'check_circle',
        tone: 'overview-stat--stable'
      },
      {
        key: 'attention',
        label: 'Attention',
        value: attentionCards.length,
        note: 'Warnings',
        icon: 'warning',
        tone: 'overview-stat--attention'
      },
      {
        key: 'urgent',
        label: 'Urgent',
        value: urgentCards.length,
        note: 'Critical Alerts',
        icon: 'emergency',
        tone: 'overview-stat--urgent'
      }
    ]
  })

  return {
    searchQuery,
    deviceCards,
    visibleDeviceCards,
    overviewStats
  }
}
