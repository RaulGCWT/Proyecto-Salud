import { defineStore } from 'pinia'
import { useRulesStore } from './rules'
import { io } from "socket.io-client"

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
    lastToast: null,
    socket: null 
  }),
  actions: {
    connectWebSocket() {
      if (this.socket) return; // Evitar reconexiones múltiples

      // Conectar con el backend en el puerto 5000
      this.socket = io('http://localhost:5000');

      this.socket.on('connect', () => {
        console.log("✅ Conectado al WebSocket del Sensor");
      });

      this.socket.on('sensor_update', (data) => {
        console.log("📥 Datos WebSocket:", data);
        
        // Sincronizar estado
        this.heartRate = data.heartRate;
        this.respiratoryRate = data.respiratoryRate;
        this.hrv = data.hrv;
        this.isOccupied = data.isOccupied;

        // Historial
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.hrHistory.push({ time: now, value: this.heartRate });
        this.hrvHistory.push({ time: now, value: this.hrv });
        this.respHistory.push({ time: now, value: this.respiratoryRate });

        if (this.hrHistory.length > 50) {
          this.hrHistory.shift(); this.hrvHistory.shift(); this.respHistory.shift();
        }

        this.checkRules();
      });

      this.socket.on('disconnect', () => console.log("❌ Desconectado del WebSocket"));
    },
    
    checkRules() {
      const rulesStore = useRulesStore()
      const now = new Date().toLocaleTimeString()

      rulesStore.rules.forEach(rule => {
        let val = rule.variable === 'hr' ? this.heartRate : rule.variable === 'hrv' ? this.hrv : this.respiratoryRate
        const isTriggered = rule.operator === '>' ? val > rule.value : val < rule.value

        if (isTriggered) {
          const newAlert = { 
            id: Date.now(), time: now, sensor: rule.name, 
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