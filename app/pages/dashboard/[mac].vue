<template>
  <div class="detail-page">
    <section class="detail-hero">
      <div class="detail-hero__copy">
        <p class="detail-hero__eyebrow">Clinical Sentinel</p>
        <h1>{{ currentTitle }}</h1>
        <p class="detail-hero__description">
          Vista detallada del dispositivo seleccionado con métricas en vivo, reglas activas y alertas recientes.
        </p>
      </div>

      <div class="detail-hero__meta">
        <div class="detail-meta-card">
          <span>MAC</span>
          <strong>{{ health.currentMac }}</strong>
        </div>
        <div class="detail-meta-card">
          <span>Patient</span>
          <strong>{{ currentPatientLabel }}</strong>
        </div>
        <div class="detail-meta-card">
          <span>Status</span>
          <strong>{{ health.isOccupied ? 'Occupied' : 'Empty' }}</strong>
        </div>
      </div>
    </section>

    <section class="detail-metrics">
      <DashboardCard
        v-for="card in dashboardCards"
        :key="card.key"
        :type="card.type"
        :title="card.title"
        :subtitle="card.subtitle"
        :main-text="card.mainText"
        :is-alert="card.isAlert"
      />
    </section>

    <section class="detail-grid">
      <div class="detail-grid__main">
        <HealthChart />
      </div>

      <aside class="detail-grid__side">
        <section class="side-panel">
          <p class="side-panel__eyebrow">Device Context</p>
          <h2 class="side-panel__title">Telemetry scope</h2>

          <div class="side-list">
            <div class="side-row">
              <span>Device ID</span>
              <strong>{{ health.currentDeviceId }}</strong>
            </div>
            <div class="side-row">
              <span>Patient</span>
              <strong>{{ currentPatientLabel }}</strong>
            </div>
            <div class="side-row">
              <span>Rules loaded</span>
              <strong>{{ scopedRules.length }}</strong>
            </div>
            <div class="side-row">
              <span>Samples buffered</span>
              <strong>{{ health.latestReadings.length }}</strong>
            </div>
          </div>
        </section>

        <section class="side-panel">
          <p class="side-panel__eyebrow">Recent alerts</p>
          <h2 class="side-panel__title">Alert queue</h2>

          <div v-if="scopedAlerts.length" class="alert-list">
            <article v-for="alert in scopedAlerts" :key="alert.id" class="alert-card">
              <div class="alert-card__top">
                <strong>{{ alert.sensor }}</strong>
                <span class="alert-card__status">{{ alert.status }}</span>
              </div>
              <p>{{ alert.message }}</p>
              <span class="alert-card__meta">{{ alert.time }} · {{ alert.dateLabel }}</span>
            </article>
          </div>

          <p v-else class="empty-copy">No hay alertas recientes para este dispositivo.</p>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import DashboardCard from '~/components/DashboardCard.vue'
import HealthChart from '~/components/HealthChart.vue'
import { useAuthStore } from '~/stores/auth'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'
import { matchesDeviceRuleScope, normalizeScopeValue } from '~/utils/telemetryScope'

const route = useRoute()
const auth = useAuthStore()
const health = useHealthStore()
const rulesStore = useRulesStore()
const RESIDENTS_API_BASE = 'http://localhost:5000/residents'

const { data: residentsData } = useFetch(RESIDENTS_API_BASE, {
  server: false,
  headers: buildBackendAuthHeaders(auth),
  default: () => []
})

function resolveMetricAlert(ruleList = [], metricId = '', currentValue = 0) {
  const normalizedValue = Number(currentValue || 0)

  return ruleList.some((rule) => {
    const parameter = String(rule.parameter || rule.variable || '').trim()
    const threshold = Number(rule.value)
    const condition = String(rule.condition || rule.operator || '').trim()

    if (metricId === 'hr' && !['hr', 'heartRate'].includes(parameter)) return false
    if (metricId === 'hrv' && parameter !== 'hrv') return false
    if (metricId === 'resp' && !['resp', 'respiratoryRate'].includes(parameter)) return false

    if (condition === '>') return normalizedValue > threshold
    if (condition === '<') return normalizedValue < threshold
    if (condition === '=' || condition === '==') return normalizedValue === threshold
    return false
  })
}

async function syncRouteScope() {
  const routeMac = normalizeScopeValue(route.params.mac)
  if (!routeMac) return

  health.setSelectedMac(routeMac)
  await Promise.all([
    rulesStore.fetchRules(),
    health.fetchDeviceInventory(),
    health.fetchAlertHistory()
  ])
  await health.fetchTelemetryHistory(200, routeMac)
}

const currentDeviceRecord = computed(() => {
  const routeMac = normalizeScopeValue(route.params.mac)

  return health.deviceInventory.find((device) => {
    const deviceMac = normalizeScopeValue(device.mac)
    const deviceId = normalizeScopeValue(device.deviceId)
    return deviceMac === routeMac || deviceId === routeMac
  }) || null
})

const residents = computed(() => Array.isArray(residentsData.value) ? residentsData.value : [])

const residentsById = computed(() => {
  const residentMap = new Map()

  for (const resident of residents.value) {
    const residentId = normalizeScopeValue(resident.id || resident.residentId)
    if (!residentId) continue
    residentMap.set(residentId, resident)
  }

  return residentMap
})

const currentPatientLabel = computed(() => {
  const currentDevice = currentDeviceRecord.value
  if (!currentDevice) {
    return 'Patient not assigned'
  }

  // Reutilizamos el mismo criterio del overview para no mostrar UUIDs internos en la UI.
  const linkedResident = residentsById.value.get(normalizeScopeValue(currentDevice.residentId))
    || residents.value.find((resident) => {
      const residentDeviceId = normalizeScopeValue(resident.deviceId)
      return residentDeviceId && (
        residentDeviceId === normalizeScopeValue(currentDevice.mac)
        || residentDeviceId === normalizeScopeValue(currentDevice.deviceId)
        || residentDeviceId === normalizeScopeValue(currentDevice.name)
      )
    })

  return linkedResident?.name || currentDevice.ownerId || currentDevice.name || 'Patient not assigned'
})

const currentTitle = computed(() => {
  const deviceId = currentDeviceRecord.value?.deviceId || health.currentDeviceId || route.params.mac
  return `${deviceId} · ${currentPatientLabel.value}`
})

const scopedRules = computed(() => {
  const routeMac = normalizeScopeValue(route.params.mac)

  return rulesStore.rules.filter(rule => matchesDeviceRuleScope(rule, {
    mac: routeMac,
    deviceId: normalizeScopeValue(currentDeviceRecord.value?.deviceId),
    side: normalizeScopeValue(health.selectedSide)
  }, currentDeviceRecord.value || {}))
})

const scopedAlerts = computed(() => {
  const routeMac = normalizeScopeValue(route.params.mac)

  return health.alertHistory
    .filter((alert) => {
      const alertMac = normalizeScopeValue(alert.mac)
      const alertDeviceId = normalizeScopeValue(alert.deviceId)
      return alertMac === routeMac || alertDeviceId === routeMac
    })
    .slice(0, 5)
})

const dashboardCards = computed(() => {
  return [
    {
      key: 'hr',
      type: 'hr',
      title: 'Heart rate',
      subtitle: 'Current average',
      mainText: `${health.heartRate || 0} BPM`,
      isAlert: resolveMetricAlert(scopedRules.value, 'hr', health.heartRate)
    },
    {
      key: 'hrv',
      type: 'hrv',
      title: 'HR variability',
      subtitle: 'Current average',
      mainText: `${health.hrv || 0} ms`,
      isAlert: resolveMetricAlert(scopedRules.value, 'hrv', health.hrv)
    },
    {
      key: 'resp',
      type: 'resp',
      title: 'Resp. rate',
      subtitle: 'Current average',
      mainText: `${health.respiratoryRate || 0} RPM`,
      isAlert: resolveMetricAlert(scopedRules.value, 'resp', health.respiratoryRate)
    },
    {
      key: 'presence',
      type: 'presence',
      title: 'Bed status',
      subtitle: 'Current occupancy',
      mainText: health.isOccupied ? 'In Use' : 'Empty',
      isAlert: false
    }
  ]
})

useHead({
  title: 'Clinical Sentinel | Device Detail'
})

onMounted(syncRouteScope)

watch(() => route.params.mac, syncRouteScope)
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(37, 89, 189, 0.08), rgba(255, 255, 255, 0.96));
  border: 1px solid var(--surface-border);
  box-shadow: 0 18px 40px var(--surface-shadow);
}

.detail-hero__eyebrow {
  margin: 0 0 8px;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2559bd;
}

.detail-hero h1 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  line-height: 1.05;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.detail-hero__description {
  margin: 14px 0 0;
  max-width: 640px;
  line-height: 1.6;
  color: var(--text-muted);
}

.detail-hero__meta {
  display: grid;
  gap: 12px;
  min-width: 260px;
}

.detail-meta-card,
.side-panel,
.alert-card {
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  box-shadow: 0 14px 30px var(--surface-shadow);
}

.detail-meta-card {
  padding: 16px 18px;
}

.detail-meta-card span,
.side-panel__eyebrow,
.side-row span,
.alert-card__meta {
  display: block;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.detail-meta-card strong,
.side-row strong,
.side-panel__title,
.alert-card strong,
.alert-card p {
  color: var(--text-main);
}

.detail-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(320px, 0.9fr);
  gap: 22px;
}

.detail-grid__side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-panel {
  padding: 22px;
}

.side-panel__eyebrow {
  margin: 0 0 8px;
  color: #2559bd;
}

.side-panel__title {
  margin: 0 0 18px;
  font-size: 1.14rem;
  font-weight: 900;
}

.side-list,
.alert-list {
  display: grid;
  gap: 12px;
}

.side-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--surface-panel);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.alert-card {
  padding: 16px;
}

.alert-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.alert-card__status {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.alert-card p {
  margin: 10px 0 8px;
  line-height: 1.5;
}

.empty-copy {
  margin: 0;
  color: var(--text-muted);
}

:global(.dark-mode) .detail-hero,
:global(.dark-mode) .detail-meta-card,
:global(.dark-mode) .side-panel,
:global(.dark-mode) .alert-card,
:global(.dark-mode) .side-row {
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.95)) !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .detail-hero h1,
:global(.dark-mode) .detail-hero__description,
:global(.dark-mode) .detail-meta-card strong,
:global(.dark-mode) .side-panel__title,
:global(.dark-mode) .side-row strong,
:global(.dark-mode) .alert-card strong,
:global(.dark-mode) .alert-card p {
  color: #f8fafc !important;
}

:global(.dark-mode) .detail-meta-card span,
:global(.dark-mode) .side-panel__eyebrow,
:global(.dark-mode) .side-row span,
:global(.dark-mode) .alert-card__meta {
  color: #94a3b8 !important;
}

@media (max-width: 1100px) {
  .detail-hero,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-hero {
    flex-direction: column;
  }

  .detail-hero__meta {
    min-width: 0;
    width: 100%;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .detail-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .detail-hero,
  .side-panel {
    padding: 18px;
  }

  .detail-metrics,
  .detail-hero__meta {
    grid-template-columns: 1fr;
  }
}
</style>
