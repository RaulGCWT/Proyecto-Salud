import { ref, computed } from 'vue'

const heartRate = ref(72)
const respiratoryRate = ref(16)
const hrv = ref(45)
const isOccupied = ref(true)
const alertHistory = ref([])
// New: Array for ECharts data
const hrHistory = ref([])

export const useHealth = () => {
  const isHRAlert = computed(() => heartRate.value > 100 || heartRate.value < 50)
  const isRespAlert = computed(() => respiratoryRate.value > 20 || respiratoryRate.value < 10)
  const isHRVAlert = computed(() => hrv.value < 20)

  const updateSensors = () => {
    heartRate.value = Math.floor(Math.random() * (115 - 45 + 1)) + 45
    respiratoryRate.value = Math.floor(Math.random() * (25 - 8 + 1)) + 8
    hrv.value = Math.floor(Math.random() * (80 - 15 + 1)) + 15
    
    // Update history for the chart (keep last 20 records)
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    hrHistory.value.push({ time: now, value: heartRate.value })
    if (hrHistory.value.length > 20) hrHistory.value.shift()
    
    checkAlerts()
  }

  const checkAlerts = () => {
    const now = new Date().toLocaleTimeString()
    if (isHRAlert.value) addAlert(now, 'Heart Rate', `${heartRate.value} BPM`, 'Critical')
    if (isRespAlert.value) addAlert(now, 'Resp. Rate', `${respiratoryRate.value} RPM`, 'Warning')
    if (isHRVAlert.value) addAlert(now, 'HRV', `${hrv.value} ms`, 'Warning')
  }

  const addAlert = (time, sensor, message, level) => {
    alertHistory.value.unshift({ time, sensor, message, level })
    if (alertHistory.value.length > 50) alertHistory.value.pop()
  }

  return {
    heartRate, respiratoryRate, hrv, isOccupied, alertHistory, hrHistory,
    isHRAlert, isRespAlert, isHRVAlert, updateSensors
  }
}