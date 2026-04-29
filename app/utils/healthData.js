const ALERT_STATUS_MAP = {
  LEIDA: 'READ',
  PENDIENTE: 'PENDING',
  READ: 'READ'
}

export const normalizeAlertStatus = (status) => {
  const value = String(status || '').trim().toUpperCase()
  return ALERT_STATUS_MAP[value] || 'PENDING'
}

export const normalizeSensorPayload = (payload) => {
  const readings = Array.isArray(payload?.readings)
    ? payload.readings
    : Array.isArray(payload?.data)
      ? payload.data
      : []

  const lastReading = payload?.lastReading || readings.at(-1) || {}

  if (!readings.length && !payload?.lastReading) return null

  return {
    mac: payload?.mac || 'unknown',
    deviceId: payload?.deviceId || 'unknown',
    deviceType: payload?.deviceType || 'Standard',
    layout: payload?.layout || 'single',
    lastReading: {
      heartRate: lastReading.heartRate,
      respiratoryRate: lastReading.respiratoryRate,
      hrv: lastReading.hrv,
      isOccupied: lastReading.isOccupied,
      side: lastReading.side,
      ts: lastReading.ts
    },
    readings
  }
}

export const buildMetricBatch = (readings, valueKey) =>
  readings.map(reading => ({
    ts: reading.ts ?? 0,
    mac: String(reading.mac || '').trim().toLowerCase(),
    deviceId: String(reading.deviceId || '').trim().toLowerCase(),
    side: String(reading.side || 'center').trim().toLowerCase(),
    time: new Date((reading.ts ?? 0) * 1000).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    value: reading[valueKey] ?? 0
  }))

export const mergeHistory = (existingHistory, incomingBatch, maxItems = 200) => {
  const merged = [...existingHistory, ...incomingBatch]
  const deduped = []
  const seen = new Set()

  for (const item of merged) {
    const key = `${String(item.mac || '').trim().toLowerCase()}-${String(item.deviceId || '').trim().toLowerCase()}-${String(item.side || '').trim().toLowerCase()}-${item.ts}-${item.value}`
    if (seen.has(key)) continue
    seen.add(key)
    deduped.push(item)
  }

  deduped.sort((a, b) => a.ts - b.ts)
  return deduped.slice(-maxItems)
}
