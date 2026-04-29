import { io } from 'socket.io-client'
import { useHealthStore } from '~/stores/health'
import { normalizeSensorPayload } from '~/utils/healthData'
import { normalizeScopeValue } from '~/utils/telemetryScope'

let socket = null

export const useHealthSocket = () => {
  const health = useHealthStore()

  const connect = () => {
    if (socket) return socket

    socket = io('http://localhost:5000')

    socket.on('sensor_update', (payload) => {
      const normalized = normalizeSensorPayload(payload)
      if (!normalized) return

      const selectedMac = normalizeScopeValue(health.selectedMac)
      const incomingMac = normalizeScopeValue(normalized.mac)

      health.ingestTelemetryPayload(normalized)

      if (!selectedMac || selectedMac === incomingMac) {
        health.checkRules(normalized.readings || [])
      }
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
