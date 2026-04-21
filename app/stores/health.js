import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { useAuthStore } from './auth'
import { getScopedOwnerId } from '~/utils/permissions'
import { normalizeAlertStatus } from '~/utils/healthData'

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
        this.alertHistory = data.map(event => ({
          id: event.id,
          time: new Date(parseFloat(event.timestamp) * 1000).toLocaleTimeString(),
          sensor: (event.parameter || 'UNTITLED').toUpperCase(),
          mac: event.mac || 'N/A',
          message: event.message || `Alert on ${event.parameter}`,
          level: 'Critical',
          status: normalizeAlertStatus(event.status)
        }))
      } catch (err) {
        console.error('Error al cargar historial de DB:', err)
      }
    },

    async setAlertStatus(alertId, status) {
      let previousStatus = 'PENDING'
      try {
        const normalized = normalizeAlertStatus(status)
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
