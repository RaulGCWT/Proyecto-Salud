import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { useAuthStore } from './auth'
import { getScopedOwnerId } from '~/utils/accessContext'
import { buildMetricBatch, mergeHistory, normalizeAlertStatus } from '~/utils/healthData'

const EVENTS_API_BASE = 'http://localhost:3001/events'
const TELEMETRY_HISTORY_API_BASE = 'http://localhost:5000/telemetry/history'
const TELEMETRY_API_BASE = 'http://localhost:5000/telemetry/latest'

const getUserOwnerId = () => {
  const auth = useAuthStore()
  return auth.user?.email || auth.user?.tenantKey || ''
}

const getScopeOwnerId = () => {
  const auth = useAuthStore()
  return getScopedOwnerId(auth.user || {})
}

const scopedHeaders = () => {
  const ownerId = getScopeOwnerId()
  return ownerId ? { 'X-Owner-Id': ownerId } : {}
}

export const useHealthStore = defineStore('health', {
  state: () => ({
    heartRate: 0,
    respiratoryRate: 0,
    hrv: 0,
    isOccupied: false,
    currentMac: 'N/A',
    currentDeviceId: 'N/A',
    latestReadings: [],
    alertHistory: [],
    hrHistory: [],
    hrvHistory: [],
    respHistory: [],
    lastToast: null
  }),
  actions: {
    async fetchAlertHistory() {
      try {
        const ownerId = getScopeOwnerId()
        const data = await $fetch(EVENTS_API_BASE, {
          params: ownerId ? { ownerId } : {},
          headers: scopedHeaders()
        })
        const events = Array.isArray(data) ? data : []

        this.alertHistory = events.map(event => {
          const eventDate = new Date(parseFloat(event.timestamp) * 1000)

          return {
            id: event.id,
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
            mac: event.mac || 'N/A',
            message: event.message || `Alert on ${event.parameter}`,
            level: 'Critical',
            status: normalizeAlertStatus(event.status)
          }
        })
      } catch (err) {
        console.error('Error al cargar historial de DB:', err)
      }
    },

    async fetchTelemetryHistory(limit = 200) {
      try {
        const ownerId = getScopeOwnerId()
        const data = await $fetch(TELEMETRY_HISTORY_API_BASE, {
          params: {
            limit,
            ...(ownerId ? { ownerId } : {})
          },
          headers: scopedHeaders()
        })

        const items = Array.isArray(data) ? [...data] : []
        if (!items.length) {
          this.hrHistory = []
          this.hrvHistory = []
          this.respHistory = []
          return
        }

        const orderedItems = items
          .map(item => ({
            ...item,
            timestamp: Number(item.timestamp || item.ts || 0)
          }))
          .sort((left, right) => left.timestamp - right.timestamp)

        const normalizedReadings = orderedItems.map(item => ({
          ts: item.timestamp,
          heartRate: item.heartRate,
          respiratoryRate: item.respiratoryRate,
          hrv: item.hrv,
          isOccupied: item.isOccupied
        }))

        this.hrHistory = mergeHistory([], buildMetricBatch(normalizedReadings, 'heartRate'))
        this.hrvHistory = mergeHistory([], buildMetricBatch(normalizedReadings, 'hrv'))
        this.respHistory = mergeHistory([], buildMetricBatch(normalizedReadings, 'respiratoryRate'))

        const latestItem = orderedItems.at(-1)
        if (latestItem) {
          this.currentMac = latestItem.mac || this.currentMac
          this.currentDeviceId = latestItem.deviceId || this.currentDeviceId
          this.heartRate = latestItem.heartRate ?? this.heartRate
          this.respiratoryRate = latestItem.respiratoryRate ?? this.respiratoryRate
          this.hrv = latestItem.hrv ?? this.hrv
          this.isOccupied = latestItem.isOccupied ?? this.isOccupied
        }
      } catch (err) {
        console.error('Error al cargar historial de telemetría:', err)
      }
    },

    async fetchLatestTelemetry() {
      try {
        const data = await $fetch(TELEMETRY_API_BASE)
        if (!data || !data.lastReading) return

        const lastReading = data.lastReading || {}
        const readings = Array.isArray(data.readings) ? data.readings : [lastReading].filter(Boolean)

        this.currentMac = data.mac || 'N/A'
        this.currentDeviceId = data.deviceId || 'N/A'
        this.heartRate = lastReading.heartRate ?? 0
        this.respiratoryRate = lastReading.respiratoryRate ?? 0
        this.hrv = lastReading.hrv ?? 0
        this.isOccupied = lastReading.isOccupied ?? false
        this.latestReadings = readings
        if (readings.length > 0) {
          this.hrHistory = mergeHistory(this.hrHistory, buildMetricBatch(readings, 'heartRate'))
          this.hrvHistory = mergeHistory(this.hrvHistory, buildMetricBatch(readings, 'hrv'))
          this.respHistory = mergeHistory(this.respHistory, buildMetricBatch(readings, 'respiratoryRate'))
        }
      } catch (err) {
        console.error('Error al cargar telemetría inicial:', err)
      }
    },

    async setAlertStatus(alertId, status) {
      let previousStatus = 'PENDING'
      try {
        const normalized = normalizeAlertStatus(status)
        const target = this.alertHistory.find(a => a.id === alertId)
        previousStatus = target?.status || 'PENDING'
        const ownerId = getScopeOwnerId()

        if (target) target.status = normalized

        const response = await $fetch(`${EVENTS_API_BASE}/${alertId}/status`, {
          method: 'PUT',
          headers: scopedHeaders(),
          body: ownerId ? { status: normalized, ownerId } : { status: normalized }
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
        const ownerId = getScopeOwnerId()
        const requestOptions = {
          method: 'DELETE',
          headers: scopedHeaders(),
          params: ownerId ? { ownerId } : {}
        }

        await $fetch(`${EVENTS_API_BASE}/${alertId}`, requestOptions)
      } catch (err) {
        console.error('Error borrando alerta:', err)
        this.alertHistory = currentHistory
        await this.fetchAlertHistory()
      }
    },

    async clearAllAlerts() {
      if (!confirm('Seguro que quieres borrar todas las alertas de la base de datos?')) return
      try {
        const ownerId = getScopeOwnerId()
        await $fetch(`${EVENTS_API_BASE}/clear`, {
          method: 'DELETE',
          params: ownerId ? { ownerId } : {},
          headers: scopedHeaders()
        })
        this.alertHistory = []
      } catch (err) {
        console.error('Error al vaciar historial:', err)
      }
    },

    checkRules() {
      const rulesStore = useRulesStore()
      rulesStore.rules.forEach(rule => {
        let val = 0
        const param = rule.parameter || rule.variable
        if (param === 'hr' || param === 'heartRate') val = this.heartRate
        else if (param === 'hrv') val = this.hrv
        else if (param === 'resp' || param === 'respiratoryRate') val = this.respiratoryRate

        const condition = rule.condition || rule.operator
        const threshold = Number(rule.value)

        let isTriggered = false
        if (condition === '>') isTriggered = val > threshold
        else if (condition === '<') isTriggered = val < threshold
        else if (condition === '==' || condition === '=') isTriggered = val == threshold

        if (isTriggered && val > 0) {
          const ownerId = getUserOwnerId()
          const newAlert = {
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            sensor: (param || 'SENSOR').toUpperCase(),
            mac: this.currentMac,
            message: `${rule.name}: ${val} detected`,
            level: 'Critical',
            status: 'PENDING',
            ownerId
          }
          this.alertHistory.unshift(newAlert)
          this.lastToast = newAlert
        }
      })
    }
  }
})
