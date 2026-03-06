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
    respHistory: [],
    lastToast: null 
  }),
  actions: {
    async updateSensors() {
      try {
        // Llamamos al contenedor de Python (ajusta la IP si es necesario)
        const response = await fetch('http://localhost:5000/sensor-data')
        const data = await response.json()

        // Actualizamos el estado con lo que viene de Python
        this.heartRate = data.heartRate
        this.respiratoryRate = data.respiratoryRate
        this.hrv = data.hrv
        this.isOccupied = data.isOccupied
        
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        
        this.hrHistory.push({ time: now, value: this.heartRate })
        this.hrvHistory.push({ time: now, value: this.hrv })
        this.respHistory.push({ time: now, value: this.respiratoryRate })
        
        if (this.hrHistory.length > 100) {
          this.hrHistory.shift(); this.hrvHistory.shift(); this.respHistory.shift();
        }
        this.checkRules()
      } catch (error) {
        console.error("Error conectando con el sensor Python:", error)
      }
    },
    checkRules() {
      const rulesStore = useRulesStore()
      const now = new Date().toLocaleTimeString()

      rulesStore.rules.forEach(rule => {
        let val = rule.variable === 'hr' ? this.heartRate : rule.variable === 'hrv' ? this.hrv : this.respiratoryRate
        const isTriggered = rule.operator === '>' ? val > rule.value : val < rule.value

        if (isTriggered) {
          const newAlert = { 
            id: Date.now(), 
            time: now, 
            sensor: rule.name, 
            message: `Value ${val} violates rule ${rule.operator}${rule.value}`,
            level: 'Critical' 
          }
          this.alertHistory.unshift(newAlert)
          this.lastToast = { ...newAlert } 
          
          if (this.alertHistory.length > 50) this.alertHistory.pop()
        }
      })
    }
  },
  persist: true
})