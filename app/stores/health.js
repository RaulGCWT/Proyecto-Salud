import { defineStore } from 'pinia'
import { useRulesStore } from './rules'

export const useHealthStore = defineStore('health', {
  state: () => ({
    heartRate: 72,
    respiratoryRate: 16,
    hrv: 45,
    isOccupied: true,
    alertHistory: [],
    hrHistory: [],
    hrvHistory: [],
    respHistory: []
  }),
  actions: {
    updateSensors() {
      // Tu lógica original de generación de datos
      this.heartRate = Math.floor(Math.random() * (115 - 45 + 1)) + 45
      this.respiratoryRate = Math.floor(Math.random() * (25 - 8 + 1)) + 8
      this.hrv = Math.floor(Math.random() * (80 - 15 + 1)) + 15
      
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      
      this.hrHistory.push({ time: now, value: this.heartRate })
      this.hrvHistory.push({ time: now, value: this.hrv })
      this.respHistory.push({ time: now, value: this.respiratoryRate })
      
      if (this.hrHistory.length > 500) {
        this.hrHistory.shift()
        this.hrvHistory.shift()
        this.respHistory.shift()
      }
      this.checkRules()
    },
    checkRules() {
      const rulesStore = useRulesStore()
      const now = new Date().toLocaleTimeString()

      // Ejecuta las reglas configuradas en la página Rules
      rulesStore.rules.forEach(rule => {
        let val = 0
        if (rule.variable === 'hr') val = this.heartRate
        if (rule.variable === 'hrv') val = this.hrv
        if (rule.variable === 'resp') val = this.respiratoryRate

        const isTriggered = rule.operator === '>' ? val > rule.value : val < rule.value

        if (isTriggered) {
          this.alertHistory.unshift({
            time: now,
            sensor: rule.name,
            message: `${val} recorded`,
            level: 'Critical'
          })
          if (this.alertHistory.length > 50) this.alertHistory.pop()
        }
      })
    }
  },
  persist: true
})