import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { useAuthStore } from './auth'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'
import { buildMetricBatch, mergeHistory, normalizeAlertStatus } from '~/utils/healthData'
import { matchesDeviceRuleScope, normalizeScopeValue } from '~/utils/telemetryScope'

const getApiBase = () => useNuxtApp().$config.public.apiBase
const MAX_TELEMETRY_RECORDS = 2000

const normalizeTelemetryRecord = (record = {}, fallback = {}) => {
  const timestamp = Number(record.ts ?? record.timestamp ?? fallback.ts ?? 0) || 0

  return {
    ...record,
    ts: timestamp,
    timestamp,
    mac: normalizeScopeValue(record.mac || fallback.mac || 'unknown'),
    deviceId: normalizeScopeValue(record.deviceId || fallback.deviceId || record.mac || fallback.mac || 'unknown'),
    side: normalizeSideValue(record.side || fallback.side || 'all'),
    heartRate: record.heartRate ?? fallback.heartRate ?? 0,
    respiratoryRate: record.respiratoryRate ?? fallback.respiratoryRate ?? 0,
    hrv: record.hrv ?? fallback.hrv ?? 0,
    isOccupied: record.isOccupied ?? fallback.isOccupied ?? false
  }
}

const mergeTelemetryRecords = (existingRecords = [], incomingRecords = []) => {
  const merged = [...existingRecords, ...incomingRecords]
  const deduped = []
  const seen = new Set()

  for (const record of merged) {
    const key = [
      normalizeScopeValue(record.mac),
      normalizeScopeValue(record.deviceId),
      normalizeSideValue(record.side),
      Number(record.ts || 0),
      Math.round(record.heartRate ?? 0),
      Math.round(record.respiratoryRate ?? 0),
      Math.round(record.hrv ?? 0),
      record.isOccupied ? '1' : '0'
    ].join('|')

    if (seen.has(key)) continue
    seen.add(key)
    deduped.push(record)
  }

  deduped.sort((left, right) => Number(left.ts || 0) - Number(right.ts || 0))
  return deduped.slice(-MAX_TELEMETRY_RECORDS)
}

const normalizeTelemetryBatch = (payload = {}) => {
  const readings = Array.isArray(payload.readings) ? payload.readings : []
  const mac = normalizeScopeValue(payload.mac || 'unknown')
  const deviceId = normalizeScopeValue(payload.deviceId || payload.mac || 'unknown')

  return readings.map(reading => normalizeTelemetryRecord(reading, {
    mac,
    deviceId
  }))
}

const getLatestBatchForScope = (records = [], scopeMac = '') => {
  const normalizedScopeMac = normalizeScopeValue(scopeMac)
  const scopedRecords = normalizedScopeMac
    ? records.filter(record => normalizeScopeValue(record.mac) === normalizedScopeMac)
    : [...records]

  if (!scopedRecords.length) return []

  const latestTimestamp = scopedRecords.at(-1)?.ts ?? 0
  return scopedRecords.filter(record => Number(record.ts || 0) === Number(latestTimestamp || 0))
}

const getTelemetryScope = (store) => ({
  mac: store.currentMac,
  deviceId: store.currentDeviceId
})

const normalizeSideValue = (value) => {
  const normalized = normalizeScopeValue(value)
  if (normalized === 'left' || normalized === 'right') return normalized
  return 'all'
}

const normalizeDeviceRecord = (device = {}) => ({
  mac: normalizeScopeValue(device.mac || device.id || ''),
  deviceId: String(device.deviceId || device.id || device.mac || '').trim(),
  name: String(device.name || device.deviceId || device.mac || '').trim(),
  type: String(device.type || 'Standard').trim(),
  connectionState: normalizeScopeValue(device.connectionState || 'offline'),
  lastHeartbeatTs: Number(device.lastHeartbeatTs || 0) || 0,
  ownerId: normalizeScopeValue(device.ownerId),
  tenantKey: normalizeScopeValue(device.tenantKey),
  residenceId: normalizeScopeValue(device.residenceId),
  area: normalizeScopeValue(device.area),
  residentId: normalizeScopeValue(device.residentId)
})

const findSelectedDeviceRecord = (store) => {
  const scopeMac = normalizeScopeValue(store.selectedMac || store.currentMac)
  const scopeDeviceId = normalizeScopeValue(store.currentDeviceId)

  if (!scopeMac && !scopeDeviceId) return null

  return store.deviceInventory.find((device) => {
    const deviceMac = normalizeScopeValue(device.mac || device.id)
    const deviceId = normalizeScopeValue(device.deviceId || device.id || device.mac)

    if (scopeMac && (deviceMac === scopeMac || deviceId === scopeMac)) return true
    if (scopeDeviceId && (deviceMac === scopeDeviceId || deviceId === scopeDeviceId)) return true
    return false
  }) || null
}

const filterTelemetryBySide = (records = [], selectedSide = 'all') => {
  const normalizedSide = normalizeSideValue(selectedSide)
  if (normalizedSide === 'all') return [...records]
  return records.filter(record => normalizeScopeValue(record.side) === normalizedSide)
}

const summarizeLatestTelemetryBatch = (records = []) => {
  if (!records.length) {
    return {
      heartRate: 0,
      respiratoryRate: 0,
      hrv: 0,
      isOccupied: false,
      latestReadings: []
    }
  }

  const latestTimestamp = Number(records.at(-1)?.ts || 0)
  const latestBatch = records.filter(record => Number(record.ts || 0) === latestTimestamp)

  const averageValue = (key) => {
    const values = latestBatch.map(item => Number(item[key] || 0)).filter(value => Number.isFinite(value))
    if (!values.length) return 0
    return values.reduce((accumulator, value) => accumulator + value, 0) / values.length
  }

  return {
    heartRate: Math.round(averageValue('heartRate')),
    respiratoryRate: Math.round(averageValue('respiratoryRate')),
    hrv: Math.round(averageValue('hrv')),
    isOccupied: latestBatch.some(item => Boolean(item.isOccupied)),
    latestReadings: latestBatch
  }
}

const scopedHeaders = () => {
  return buildBackendAuthHeaders(useAuthStore())
}

export const useHealthStore = defineStore('health', {
  state: () => ({
    heartRate: 0,
    respiratoryRate: 0,
    hrv: 0,
    isOccupied: false,
    currentMac: 'N/A',
    currentDeviceId: 'N/A',
    selectedMac: '',
    selectedSide: 'all',
    telemetryRecords: [],
    deviceInventory: [],
    latestReadings: [],
    alertHistory: [],
    hrHistory: [],
    hrvHistory: [],
    respHistory: [],
    lastToast: null
  }),
  actions: {
    setSelectedMac(mac) {
      this.selectedMac = normalizeScopeValue(mac)
      this.selectedSide = 'all'
      this.rebuildSelectedTelemetrySnapshot()
    },

    setSelectedSide(side) {
      this.selectedSide = normalizeSideValue(side)
      this.rebuildSelectedTelemetrySnapshot()
    },

    rebuildSelectedTelemetrySnapshot() {
      const scopeMac = normalizeScopeValue(this.selectedMac)
      const scopedRecords = scopeMac
        ? this.telemetryRecords.filter(record => normalizeScopeValue(record.mac) === scopeMac)
        : [...this.telemetryRecords]

      const sideScopedRecords = filterTelemetryBySide(scopedRecords, this.selectedSide)

      if (!sideScopedRecords.length) {
        this.currentMac = scopeMac || 'N/A'
        this.currentDeviceId = 'N/A'
        this.heartRate = 0
        this.respiratoryRate = 0
        this.hrv = 0
        this.isOccupied = false
        this.latestReadings = []
        this.hrHistory = []
        this.hrvHistory = []
        this.respHistory = []
        return
      }

      const orderedRecords = [...sideScopedRecords].sort((left, right) => Number(left.ts || 0) - Number(right.ts || 0))
      const latestRecord = orderedRecords.at(-1)
      const batchSummary = summarizeLatestTelemetryBatch(orderedRecords)

      this.currentMac = latestRecord.mac || scopeMac || 'N/A'
      this.currentDeviceId = latestRecord.deviceId || latestRecord.mac || 'N/A'
      this.heartRate = batchSummary.heartRate
      this.respiratoryRate = batchSummary.respiratoryRate
      this.hrv = batchSummary.hrv
      this.isOccupied = batchSummary.isOccupied
      this.latestReadings = batchSummary.latestReadings
      this.hrHistory = mergeHistory([], buildMetricBatch(orderedRecords, 'heartRate'))
      this.hrvHistory = mergeHistory([], buildMetricBatch(orderedRecords, 'hrv'))
      this.respHistory = mergeHistory([], buildMetricBatch(orderedRecords, 'respiratoryRate'))
    },

    ingestTelemetryPayload(payload, { selectIfEmpty = false } = {}) {
      const normalizedBatch = normalizeTelemetryBatch(payload)
      if (!normalizedBatch.length) return []

      this.telemetryRecords = mergeTelemetryRecords(this.telemetryRecords, normalizedBatch)

      if (!this.selectedMac) {
        const fallbackMac = normalizeScopeValue(payload.mac || normalizedBatch.at(-1)?.mac || '')
        if (fallbackMac && (selectIfEmpty || this.telemetryRecords.length)) {
          this.selectedMac = fallbackMac
        }
      }

      this.rebuildSelectedTelemetrySnapshot()
      return normalizedBatch
    },

    async fetchAlertHistory() {
      try {
        const data = await $fetch(`${getApiBase()}/events`, {
          headers: scopedHeaders()
        })
        const events = Array.isArray(data) ? data : []

        this.alertHistory = events.map(event => {
          const eventDate = new Date(parseFloat(event.timestamp) * 1000)
          const numericTimestamp = Number(event.timestamp) || 0

          return {
            id: event.id || `${event.mac || ''}_${event.parameter || ''}_${numericTimestamp}`,
            timestamp: numericTimestamp,
            time: eventDate.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit'
            }),
            dateLabel: eventDate.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            }),
            sensor: (event.parameter || 'UNTITLED').toUpperCase(),
            mac: normalizeScopeValue(event.mac || 'N/A'),
            deviceId: normalizeScopeValue(event.deviceId || event.mac || 'N/A'),
            side: normalizeSideValue(event.side || 'all'),
            message: event.message || `Alert on ${event.parameter}`,
            level: 'Critical',
            status: normalizeAlertStatus(event.status)
          }
        })
      } catch (err) {
        console.error('Error al cargar historial de DB:', err)
      }
    },

    async fetchTelemetryHistory(limit = 200, mac = '') {
      try {
        const scopeMac = normalizeScopeValue(mac || this.selectedMac || this.currentMac || this.deviceInventory[0]?.mac)
        if (!scopeMac) return

        const data = await $fetch(`${getApiBase()}/telemetry/history`, {
          params: { limit, mac: scopeMac },
          headers: scopedHeaders()
        })

        const items = Array.isArray(data) ? data : []
        this.telemetryRecords = mergeTelemetryRecords([], items.map(item => normalizeTelemetryRecord(item)))

        if (!this.selectedMac && this.telemetryRecords.length) {
          const latestItem = this.telemetryRecords.at(-1)
          this.selectedMac = latestItem?.mac || ''
        }

        this.rebuildSelectedTelemetrySnapshot()
      } catch (err) {
        console.error('Error al cargar historial de telemetrÃ­a:', err)
      }
    },

    async fetchTelemetryHistoryForInventory(limit = 200) {
      try {
        const inventoryMacs = Array.from(new Set(
          (this.deviceInventory || [])
            .map(device => normalizeScopeValue(device.mac || device.deviceId))
            .filter(Boolean)
        ))

        if (!inventoryMacs.length) {
          this.telemetryRecords = []
          this.rebuildSelectedTelemetrySnapshot()
          return
        }

        const responses = await Promise.all(
          inventoryMacs.map((mac) => $fetch(`${getApiBase()}/telemetry/history`, {
            params: { limit, mac },
            headers: scopedHeaders()
          }).catch(() => []))
        )

        const mergedItems = responses.flatMap((items) => {
          const safeItems = Array.isArray(items) ? items : []
          return safeItems.map(item => normalizeTelemetryRecord(item))
        })

        this.telemetryRecords = mergeTelemetryRecords([], mergedItems)

        if (!this.selectedMac && this.telemetryRecords.length) {
          const latestItem = this.telemetryRecords.at(-1)
          this.selectedMac = latestItem?.mac || inventoryMacs[0] || ''
        }

        this.rebuildSelectedTelemetrySnapshot()
      } catch (err) {
        console.error('Error al cargar historial global de telemetria:', err)
      }
    },

    async fetchDeviceInventory() {
      try {
        const data = await $fetch(`${getApiBase()}/devices`, {
          headers: scopedHeaders()
        })

        const items = Array.isArray(data) ? data : []
        this.deviceInventory = items.map(normalizeDeviceRecord)
      } catch (err) {
        console.error('Error al cargar inventario de dispositivos:', err)
      }
    },

    async fetchLatestTelemetry() {
      try {
        const data = await $fetch(`${getApiBase()}/telemetry/latest`, {
          headers: scopedHeaders()
        })
        if (!data || !data.lastReading) return

        this.ingestTelemetryPayload(data, { selectIfEmpty: true })
      } catch (err) {
        console.error('Error al cargar telemetrÃ­a inicial:', err)
      }
    },

    async setAlertStatus(alertId, status) {
      let previousStatus = 'PENDING'
      try {
        const normalized = normalizeAlertStatus(status)
        const target = this.alertHistory.find(a => a.id === alertId)
        previousStatus = target?.status || 'PENDING'

        if (target) target.status = normalized

        const response = await $fetch(`${getApiBase()}/events/${alertId}/status`, {
          method: 'PUT',
          headers: scopedHeaders(),
          body: { status: normalized }
        })

        if (response?.status) {
          const saved = normalizeAlertStatus(response.status)
          if (target) target.status = saved
        }

        await this.fetchAlertHistory()
      } catch (err) {
        const target = this.alertHistory.find(a => a.id === alertId)
        if (target) target.status = previousStatus || 'PENDING'
        console.error('Error actualizando estado de alerta:', err)
      }
    },

    async deleteAlert(alertId) {
      if (!alertId) return

      const currentHistory = [...this.alertHistory]
      this.alertHistory = this.alertHistory.filter(alert => alert.id !== alertId)

      try {
        const requestOptions = {
          method: 'DELETE',
          headers: scopedHeaders()
        }

        await $fetch(`${getApiBase()}/events/${alertId}`, requestOptions)
      } catch (err) {
        console.error('Error borrando alerta:', err)
        this.alertHistory = currentHistory
        await this.fetchAlertHistory()
      }
    },

    async clearAllAlerts() {
      try {
        await $fetch(`${getApiBase()}/events/clear`, {
          method: 'DELETE',
          headers: scopedHeaders()
        })
        this.alertHistory = []
      } catch (err) {
        console.error('Error al vaciar historial:', err)
        throw err
      }
    },

    checkRules(readings = []) {
      const rulesStore = useRulesStore()
      const selectedDevice = findSelectedDeviceRecord(this) || {}
      const inputReadings = Array.isArray(readings) && readings.length
        ? readings
        : (Array.isArray(this.latestReadings) ? this.latestReadings : [])

      inputReadings.forEach((reading) => {
        const readingScope = {
          ...getTelemetryScope(this),
          mac: normalizeScopeValue(reading.mac || this.currentMac),
          deviceId: normalizeScopeValue(reading.deviceId || this.currentDeviceId),
          side: normalizeSideValue(reading.side)
        }

        rulesStore.rules.forEach(rule => {
          if (!matchesDeviceRuleScope(rule, readingScope, selectedDevice)) return

          let value = 0
          const parameter = rule.parameter || rule.variable
          if (parameter === 'hr' || parameter === 'heartRate') value = reading.heartRate ?? 0
          else if (parameter === 'hrv') value = reading.hrv ?? 0
          else if (parameter === 'resp' || parameter === 'respiratoryRate') value = reading.respiratoryRate ?? 0

          const condition = rule.condition || rule.operator
          const threshold = Number(rule.value)

          let isTriggered = false
          if (condition === '>') isTriggered = value > threshold
          else if (condition === '<') isTriggered = value < threshold
          else if (condition === '==' || condition === '=') isTriggered = value == threshold

          if (isTriggered && value > 0) {
            const newAlert = {
              id: Date.now(),
              timestamp: Math.floor(Date.now() / 1000),
              time: new Date().toLocaleTimeString(),
              sensor: (parameter || 'SENSOR').toUpperCase(),
              mac: normalizeScopeValue(reading.mac || this.currentMac || 'N/A'),
              deviceId: normalizeScopeValue(reading.deviceId || this.currentDeviceId || reading.mac || 'N/A'),
              side: normalizeSideValue(reading.side),
              message: `${rule.name}: ${value} detected`,
              level: 'Critical',
              status: 'PENDING',
              ownerId: ''
            }
            this.alertHistory.unshift(newAlert)
            this.lastToast = newAlert
          }
        })
      })
    }
  }
})
