import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { io } from "socket.io-client"

export const useHealthStore = defineStore('health', {
  state: () => ({
    heartRate: 0,
    respiratoryRate: 0,
    hrv: 0,
    isOccupied: false,
    alertHistory: [],
    hrHistory: [],
    hrvHistory: [],
    respHistory: [],
    lastToast: null,
    socket: null
  }),
  actions: {
    connectWebSocket() {
      if (this.socket) return
      this.socket = io('http://localhost:5000')

      this.socket.on('sensor_update', (data) => {
        this.heartRate = data.heartRate
        this.respiratoryRate = data.respiratoryRate
        this.hrv = data.hrv
        this.isOccupied = data.isOccupied
        
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        this.hrHistory.push({ time: now, value: this.heartRate })
        this.hrvHistory.push({ time: now, value: this.hrv })
        this.respHistory.push({ time: now, value: this.respiratoryRate })
        
        if (this.hrHistory.length > 50) {
          this.hrHistory.shift(); this.hrvHistory.shift(); this.respHistory.shift();
        }
        this.checkRules()
      })
    },
    checkRules() {
      const rulesStore = useRulesStore()
      rulesStore.rules.forEach(rule => {
        // Obtenemos el valor actual basado en el parámetro de la regla
        let val = 0
        const param = rule.parameter || rule.variable // Soporta ambos por si acaso
        
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
          const newAlert = { 
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            sensor: (param || 'UNKNOWN').toUpperCase(),
            message: `${rule.name}: ${val} detectado`,
            level: 'Critical'
          }
          this.alertHistory.unshift(newAlert)
          this.lastToast = newAlert
        }
      })
    }
  }
})