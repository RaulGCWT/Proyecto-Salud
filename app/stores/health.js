import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { useAuthStore } from './auth'
import { io } from 'socket.io-client'
import { getScopedOwnerId } from '~/utils/permissions'

const EVENTS_API_BASE = 'http://localhost:3001/MonitoringEvents'

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
    lastToast: null,
    socket: null
  }),
  actions: {
    normalizeAlertStatus(status) {
      const value = String(status || '').toUpperCase()
      if (value === 'LEIDA') return 'READ'
      if (value === 'PENDIENTE') return 'PENDING'
      if (value === 'READ') return 'READ'
      return 'PENDING'
    },

    async fetchAlertHistory() {
      try {
        const ownerId = getScopeOwnerId()
        const data = await $fetch(EVENTS_API_BASE, {
          params: ownerId ? { ownerId } : {},
          headers: scopedHeaders()
        })
        this.alertHistory = data.map(event => ({
          id: event.id,
          time: new Date(parseFloat(event.timestamp) * 1000).toLocaleTimeString(),
          sensor: (event.parameter || 'UNTITLED').toUpperCase(),
          mac: event.mac || 'N/A',
          message: event.message || `Alert on ${event.parameter}`,
          level: 'Critical',
          status: this.normalizeAlertStatus(event.status)
        }))
      } catch (err) {
        console.error('Error al cargar historial de DB:', err)
      }
    },

    async setAlertStatus(alertId, status) {
      let previousStatus = 'PENDING'
      try {
        const normalized = this.normalizeAlertStatus(status)
        const target = this.alertHistory.find(a => a.id === alertId)
        previousStatus = target?.status || 'PENDING'
        const ownerId = getUserOwnerId()

        if (target) target.status = normalized

        const response = await $fetch(`${EVENTS_API_BASE}/${alertId}/status`, {
          method: 'PUT',
          headers: scopedHeaders(),
          body: {
            status: normalized,
            ownerId
          }
        })

        if (response?.status) {
          const saved = this.normalizeAlertStatus(response.status)
          if (target) target.status = saved
        }

        await this.fetchAlertHistory()
      } catch (err) {
        const target = this.alertHistory.find(a => a.id === alertId)
        if (target) target.status = previousStatus || 'PENDING'
        console.error('Error actualizando estado de alerta:', err)
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

    connectWebSocket() {
      if (this.socket) return
      this.socket = io('http://localhost:5000')

      this.socket.on('sensor_update', (data) => {
        const lastReading = data.lastReading || {}
        const readings = Array.isArray(data.readings) ? data.readings : []

        this.heartRate = lastReading.heartRate ?? 0
        this.respiratoryRate = lastReading.respiratoryRate ?? 0
        this.hrv = lastReading.hrv ?? 0
        this.isOccupied = lastReading.isOccupied ?? false
        this.currentMac = data.mac || 'N/A'
        this.currentDeviceId = data.deviceId || 'N/A'
        this.latestReadings = readings

        if (readings.length > 0) {
          const hrBatch = readings.map(reading => ({
            ts: reading.ts ?? 0,
            time: new Date((reading.ts ?? 0) * 1000).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            }),
            value: reading.heartRate ?? 0
          }))
          const hrvBatch = readings.map(reading => ({
            ts: reading.ts ?? 0,
            time: new Date((reading.ts ?? 0) * 1000).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            }),
            value: reading.hrv ?? 0
          }))
          const respBatch = readings.map(reading => ({
            ts: reading.ts ?? 0,
            time: new Date((reading.ts ?? 0) * 1000).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            }),
            value: reading.respiratoryRate ?? 0
          }))

          this.hrHistory = this.mergeHistory(this.hrHistory, hrBatch)
          this.hrvHistory = this.mergeHistory(this.hrvHistory, hrvBatch)
          this.respHistory = this.mergeHistory(this.respHistory, respBatch)
        }
        this.checkRules()
      })
    },

    mergeHistory(existingHistory, incomingBatch) {
      const merged = [...existingHistory, ...incomingBatch]
      const deduped = []
      const seen = new Set()

      for (const item of merged) {
        const key = `${item.ts}-${item.value}`
        if (seen.has(key)) continue
        seen.add(key)
        deduped.push(item)
      }

      deduped.sort((a, b) => a.ts - b.ts)
      return deduped.slice(-200)
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
