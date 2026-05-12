import { io } from 'socket.io-client'
import { useHealthStore } from '~/stores/health'
import { useAuthStore } from '~/stores/auth'
import { normalizeSensorPayload } from '~/utils/healthData'
import { normalizeScopeValue } from '~/utils/telemetryScope'

let socket = null

export const useHealthSocket = () => {
  const health = useHealthStore()
  const auth = useAuthStore()

  const connect = () => {
    const token = auth.idToken || auth.accessToken || ''
    if (!token) return null

    if (socket?.connected) return socket

    if (socket) {
      socket.disconnect()
      socket = null
    }

    const apiBase = useNuxtApp().$config.public.apiBase
    socket = io(apiBase, {
      auth: {
        token
      }
    })

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
