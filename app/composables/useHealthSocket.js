import { io } from 'socket.io-client'
import { useHealthStore } from '~/stores/health'
import { buildMetricBatch, mergeHistory, normalizeSensorPayload } from '~/utils/healthData'

let socket = null

export const useHealthSocket = () => {
  const health = useHealthStore()

  const connect = () => {
    if (socket) return socket

    socket = io('http://localhost:5000')

    socket.on('sensor_update', (payload) => {
      const normalized = normalizeSensorPayload(payload)
      if (!normalized) return

      const { lastReading, readings } = normalized

      health.heartRate = lastReading.heartRate ?? 0
      health.respiratoryRate = lastReading.respiratoryRate ?? 0
      health.hrv = lastReading.hrv ?? 0
      health.isOccupied = lastReading.isOccupied ?? false
      health.currentMac = normalized.mac || 'N/A'
      health.currentDeviceId = normalized.deviceId || 'N/A'
      health.latestReadings = readings

      if (readings.length > 0) {
        health.hrHistory = mergeHistory(health.hrHistory, buildMetricBatch(readings, 'heartRate'))
        health.hrvHistory = mergeHistory(health.hrvHistory, buildMetricBatch(readings, 'hrv'))
        health.respHistory = mergeHistory(health.respHistory, buildMetricBatch(readings, 'respiratoryRate'))
      }

      health.checkRules()
    })

    return socket
  }

  const disconnect = () => {
    if (!socket) return
    socket.disconnect()
    socket = null
  }

  return {
    connect,
    disconnect
  }
}
