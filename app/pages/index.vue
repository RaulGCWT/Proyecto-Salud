<template>
  <div class="dashboard-page">
    <section class="device-tabs-shell">
      <div class="device-tabs-header">
        <p class="panel-eyebrow">Device switching</p>
        <h2 class="device-tabs-title">Choose active MAC</h2>
      </div>

      <div class="device-tabs" role="tablist" aria-label="Device selector">
        <button
          v-for="option in deviceOptions"
          :key="option.value || option.label"
          type="button"
          class="device-tab"
          :class="{ 'device-tab--active': selectedMacModel === option.value }"
          :disabled="!option.value"
          role="tab"
          :aria-selected="selectedMacModel === option.value ? 'true' : 'false'"
          @click="selectedMacModel = option.value"
        >
          <span class="device-tab__label">MAC</span>
          <span class="device-tab__value">{{ option.label }}</span>
        </button>
      </div>
    </section>

    <section class="hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">Clinical Sentinel</p>
        <h1>Monitoring Overview</h1>
        <p class="hero-description">
          Real biometrics from <strong>{{ currentDeviceLabel }}</strong> with synchronized telemetry, alert handling and occupancy state.
        </p>

        <div class="hero-pills">
          <span class="status-pill status-pill-live">
            <span class="status-dot"></span>
            System Status: Live
          </span>
          <span class="status-pill status-pill-soft">
            {{ health.latestReadings.length }} samples buffered
          </span>
          <span class="status-pill status-pill-soft">
            {{ scopedRules.length }} active rules
          </span>
        </div>
      </div>

      <div class="hero-summary">
        <div class="summary-box">
          <span class="summary-label">Telemetry source</span>
          <strong>{{ health.currentMac }}</strong>
        </div>
        <div class="summary-box">
          <span class="summary-label">Occupancy</span>
          <strong>{{ health.isOccupied ? 'Occupied' : 'Empty' }}</strong>
        </div>
        <div class="summary-box">
          <span class="summary-label">Open alerts</span>
          <strong>{{ openAlerts.length }}</strong>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <DashboardCard
        v-for="card in dashboardCards"
        :key="card.key"
        :type="card.type"
        :title="card.title"
        :subtitle="card.subtitle"
        :main-text="card.mainText"
        :is-alert="card.isAlert"
        :description="card.description"
      />
    </section>

    <section class="dashboard-grid">
      <div class="main-column">
        <div class="chart-panel">
          <HealthChart />
        </div>
      </div>

      <aside class="side-column">
        <div class="panel side-panel">
          <div class="panel-header compact">
            <div>
              <p class="panel-eyebrow">Bed overview</p>
              <h3 class="panel-title">Telemetry context</h3>
            </div>
          </div>

          <div class="info-list">
            <div class="info-row">
              <span>Device ID</span>
              <strong>{{ health.currentDeviceId }}</strong>
            </div>
            <div class="info-row">
              <span>MAC Address</span>
              <strong>{{ health.currentMac }}</strong>
            </div>
            <div class="info-row" v-if="isDoubleBedDevice">
              <span>Side view</span>
              <strong>{{ selectedSideLabel }}</strong>
            </div>
            <div class="info-row">
              <span>Bed state</span>
              <strong :class="health.isOccupied ? 'state-on' : 'state-off'">
                {{ health.isOccupied ? 'Occupied' : 'Empty' }}
              </strong>
            </div>
            <div class="info-row">
              <span>Buffered samples</span>
              <strong>{{ health.latestReadings.length }}</strong>
            </div>
          </div>
        </div>

        <div class="panel side-panel">
          <div class="panel-header compact">
            <div>
              <p class="panel-eyebrow">Recent alerts</p>
              <h3 class="panel-title">Alert queue</h3>
            </div>
          </div>

          <div v-if="openAlerts.length" class="alert-list">
            <article v-for="alert in openAlerts" :key="alert.id" class="alert-item">
              <div class="alert-top">
                <strong>{{ alert.sensor }}</strong>
                <span :class="['alert-badge', alert.status === 'READ' ? 'alert-read' : 'alert-open']">
                  {{ alert.status }}
                </span>
              </div>
              <p>{{ alert.message }}</p>
              <span class="alert-meta">{{ alert.time }} · {{ alert.mac }}{{ alert.side && alert.side !== 'all' ? ` · ${alert.side}` : '' }}</span>
            </article>
          </div>
          <p v-else class="empty-state">No alerts available right now.</p>
        </div>

        <div class="panel side-panel">
          <div class="panel-header compact">
            <div>
              <p class="panel-eyebrow">System snapshot</p>
              <h3 class="panel-title">Monitoring status</h3>
            </div>
          </div>

          <div class="status-grid">
            <div class="status-card">
              <span class="summary-label">Latest alert</span>
              <strong>{{ latestAlert?.time || 'No alerts yet' }}</strong>
            </div>
            <div class="status-card">
              <span class="summary-label">Rules loaded</span>
              <strong>{{ scopedRules.length }}</strong>
            </div>
            <div class="status-card">
              <span class="summary-label">Telemetry state</span>
              <strong :class="hasLiveData ? 'state-on' : 'state-off'">
                {{ hasLiveData ? 'Receiving data' : 'Waiting for telemetry' }}
              </strong>
            </div>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { matchesDeviceRuleScope, normalizeScopeValue } from '~/utils/telemetryScope'

const health = useHealthStore()
const rulesStore = useRulesStore()

const selectedMacModel = computed({
  get: () => health.selectedMac,
  set: value => health.setSelectedMac(value)
})

const deviceOptions = computed(() => {
  const latestByMac = new Map()

  for (const record of health.telemetryRecords) {
    const mac = normalizeScopeValue(record.mac)
    if (!mac) continue

    const current = latestByMac.get(mac)
    if (!current || Number(record.ts || 0) >= Number(current.ts || 0)) {
      latestByMac.set(mac, record)
    }
  }

  const options = Array.from(latestByMac.values())
    .sort((left, right) => Number(right.ts || 0) - Number(left.ts || 0))
    .map((record) => {
      const mac = normalizeScopeValue(record.mac)
      const deviceId = String(record.deviceId || '').trim()
      const label = deviceId && deviceId !== mac ? `${deviceId} · ${mac}` : mac

      return {
        value: mac,
        label: label || mac
      }
    })

  if (!options.length) {
    return [{ value: '', label: 'No devices available' }]
  }

  return options
})

const selectedDeviceRecord = computed(() => {
  const scopeMac = normalizeScopeValue(health.selectedMac || health.currentMac)
  const scopeDeviceId = normalizeScopeValue(health.currentDeviceId)

  return health.deviceInventory.find((device) => {
    const deviceMac = normalizeScopeValue(device.mac || device.id)
    const deviceId = normalizeScopeValue(device.deviceId || device.id || device.mac)

    if (scopeMac && (deviceMac === scopeMac || deviceId === scopeMac)) return true
    if (scopeDeviceId && (deviceMac === scopeDeviceId || deviceId === scopeDeviceId)) return true
    return false
  }) || null
})

const isDoubleBedDevice = computed(() =>
  String(selectedDeviceRecord.value?.type || '').trim().toLowerCase().includes('double')
)

const selectedSideLabel = computed(() => {
  const side = normalizeScopeValue(health.selectedSide)
  if (side === 'left') return 'Left'
  if (side === 'right') return 'Right'
  return isDoubleBedDevice.value ? 'All sides' : 'Single side'
})

const getAverageFromHistory = (history = [], limit = 10) => {
  const recentValues = [...history]
    .slice(-Math.max(1, limit))
    .map(point => Number(point.value))
    .filter(value => Number.isFinite(value))

  if (!recentValues.length) return 0

  const total = recentValues.reduce((sum, value) => sum + value, 0)
  return Math.round(total / recentValues.length)
}

const scopedRules = computed(() => {
  const telemetryScope = {
    mac: normalizeScopeValue(health.selectedMac || health.currentMac),
    deviceId: normalizeScopeValue(health.currentDeviceId)
  }

  return rulesStore.rules.filter(rule => matchesDeviceRuleScope(rule, telemetryScope, selectedDeviceRecord.value || {}))
})

useHead({
  title: 'Clinical Sentinel | Dashboard'
})

onMounted(async () => {
  await Promise.all([
    rulesStore.fetchRules(),
    health.fetchDeviceInventory(),
    health.fetchAlertHistory()
  ])
})

const hasRuleAlert = (variable, currentValue) => {
  const numericValue = Number(currentValue)

  return scopedRules.value.some((rule) => {
    const ruleVariable = rule.parameter || rule.variable
    if (ruleVariable !== variable) return false

    const threshold = Number(rule.value)
    const condition = rule.condition || rule.operator

    if (condition === '>') return numericValue > threshold
    if (condition === '<') return numericValue < threshold
    if (condition === '==' || condition === '=') return numericValue == threshold
    return false
  })
}

const dashboardCards = computed(() => {
  const averageHeartRate = getAverageFromHistory(health.hrHistory) || health.heartRate
  const averageHrv = getAverageFromHistory(health.hrvHistory) || health.hrv
  const averageRespiratoryRate = getAverageFromHistory(health.respHistory) || health.respiratoryRate

  const heartRateAlert = hasRuleAlert('hr', averageHeartRate)
  const hrvAlert = hasRuleAlert('hrv', averageHrv)
  const respiratoryAlert = hasRuleAlert('resp', averageRespiratoryRate)

  return [
    {
      key: 'hr',
      type: 'hr',
      title: 'Heart rate',
      subtitle: 'Average Heart rate',
      mainText: `${averageHeartRate} BPM`,
      isAlert: heartRateAlert,
      description: heartRateAlert ? 'Average out of range' : 'Average of recent samples'
    },
    {
      key: 'hrv',
      type: 'hrv',
      title: 'HR variability',
      subtitle: 'Average HRV',
      mainText: `${averageHrv} ms`,
      isAlert: hrvAlert,
      description: hrvAlert ? 'Average out of range' : 'Average of recent samples'
    },
    {
      key: 'resp',
      type: 'resp',
      title: 'Resp. rate',
      subtitle: 'Average respiratory rate',
      mainText: `${averageRespiratoryRate} RPM`,
      isAlert: respiratoryAlert,
      description: respiratoryAlert ? 'Average out of range' : 'Average of recent samples'
    },
    {
      key: 'presence',
      type: 'presence',
      title: 'Bed Status',
      subtitle: 'Occupancy status',
      mainText: health.isOccupied ? 'In Use' : 'Empty',
      isAlert: false,
      description: 'Occupancy'
    }
  ]
})

const scopedAlertHistory = computed(() => {
  const selectedMac = normalizeScopeValue(health.selectedMac || health.currentMac)
  const selectedSide = normalizeScopeValue(health.selectedSide)
  if (!selectedMac) return health.alertHistory

  return health.alertHistory.filter(alert => {
    const alertMac = normalizeScopeValue(alert.mac)
    const alertDeviceId = normalizeScopeValue(alert.deviceId)
    const alertSide = normalizeScopeValue(alert.side)
    const matchesDevice = alertMac === selectedMac || alertDeviceId === selectedMac
    const matchesSide = selectedSide === 'all' || !alertSide || alertSide === selectedSide
    return matchesDevice && matchesSide
  })
})

const recentAlerts = computed(() => scopedAlertHistory.value.slice(0, 4))
const openAlerts = computed(() => recentAlerts.value.filter(alert => alert.status !== 'READ'))
const latestAlert = computed(() => scopedAlertHistory.value[0] || null)
const currentDeviceLabel = computed(() => health.currentDeviceId !== 'N/A' ? health.currentDeviceId : health.currentMac)
const hasLiveData = computed(() => health.latestReadings.length > 0 || health.heartRate > 0 || health.hrv > 0 || health.respiratoryRate > 0)
</script>

<style scoped>
.dashboard-page { display: flex; flex-direction: column; gap: 24px; }
.dashboard-page :deep(*) {
  box-sizing: border-box;
}

:global(.dark-mode) .dashboard-page {
  color: var(--text-main);
}

:global(.dark-mode) .hero-panel,
:global(.dark-mode) .panel,
:global(.dark-mode) .summary-box,
:global(.dark-mode) .status-card,
:global(.dark-mode) .info-row,
:global(.dark-mode) .alert-item,
:global(.dark-mode) .chart-frame {
  background: var(--surface-card-soft) !important;
  border-color: var(--surface-border) !important;
  box-shadow: 0 18px 40px var(--surface-shadow) !important;
  background-image: none !important;
}

:global(.dark-mode) .hero-panel {
  background: linear-gradient(135deg, rgba(2, 6, 23, 0.99), rgba(15, 23, 42, 0.97)) !important;
  background-image: none !important;
}

:global(.dark-mode) .hero-copy h1,
:global(.dark-mode) .panel-title,
:global(.dark-mode) .summary-box strong,
:global(.dark-mode) .status-card strong,
:global(.dark-mode) .alert-item p,
:global(.dark-mode) .chart-title {
  color: #f8fafc !important;
}

:global(.dark-mode) .hero-description,
:global(.dark-mode) .summary-label,
:global(.dark-mode) .panel-eyebrow,
:global(.dark-mode) .panel-subtitle,
:global(.dark-mode) .info-row span,
:global(.dark-mode) .alert-meta,
:global(.dark-mode) .empty-state,
:global(.dark-mode) .chart-subtitle,
:global(.dark-mode) .summary-label,
:global(.dark-mode) .card-label {
  color: #94a3b8 !important;
}

:global(.dark-mode) .status-pill-live {
  background: rgba(16, 185, 129, 0.14) !important;
  color: #a7f3d0 !important;
  border-color: rgba(52, 211, 153, 0.2) !important;
}

:global(.dark-mode) .status-pill-soft {
  background: var(--surface-card-tinted) !important;
  color: #dbeafe !important;
  border-color: rgba(96, 165, 250, 0.18) !important;
}

:global(.dark-mode) .panel-eyebrow,
:global(.dark-mode) .eyebrow {
  color: #60a5fa !important;
}

:global(.dark-mode) .control-btn {
  background: rgba(2, 6, 23, 0.9) !important;
  border-color: rgba(51, 65, 85, 0.78) !important;
  color: #cbd5e1 !important;
}

:global(.dark-mode) .control-btn.active {
  background: linear-gradient(135deg, #0f172a, #1d4ed8) !important;
  color: #f8fafc !important;
}

:global(.dark-mode) .legend-item {
  color: #94a3b8 !important;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: var(--surface-hero);
  box-shadow: 0 18px 50px var(--surface-shadow);
}
.hero-copy { flex: 1 1 560px; }
.eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.2em; font-size: 0.72rem; font-weight: 800; color: #2559bd; }
.hero-copy h1 { margin: 0; font-size: clamp(2rem, 3vw, 3rem); line-height: 1.05; font-weight: 900; color: var(--text-main); }
.hero-description { margin: 14px 0 0; max-width: 700px; color: var(--text-muted); font-size: 1rem; line-height: 1.7; }
.hero-pills { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 800;
  border: 1px solid transparent;
}
.status-pill-live { background: rgba(16, 185, 129, 0.12); color: #047857; border-color: rgba(16, 185, 129, 0.24); }
.status-pill-soft { background: rgba(37, 89, 189, 0.08); color: #2559bd; border-color: rgba(37, 89, 189, 0.14); }
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.15);
}
.hero-summary {
  flex: 0 0 280px;
  display: grid;
  gap: 12px;
}
.summary-box {
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: var(--surface-panel);
  backdrop-filter: blur(10px);
}

:global(.dark-mode) .summary-box {
  background: var(--surface-card) !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .hero-summary .summary-box {
  background: rgba(2, 6, 23, 0.98) !important;
  border-color: var(--surface-border) !important;
  background-image: none !important;
}
.summary-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 800;
}
.summary-box strong, .status-card strong { color: var(--text-main); font-size: 1rem; }
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 18px;
}
.device-tabs-shell {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px 16px;
  border-radius: 24px;
  border: 1px solid var(--border-color);
  background: var(--surface-panel-strong);
  box-shadow: 0 18px 40px var(--surface-shadow);
}
.device-tabs-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.device-tabs-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 900;
  letter-spacing: -0.03em;
  color: var(--text-main);
}
.device-tabs {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 2px 4px;
  scrollbar-width: thin;
}
.device-tabs::-webkit-scrollbar {
  height: 8px;
}
.device-tabs::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.36);
}
.device-tab {
  position: relative;
  flex: 0 0 auto;
  min-width: 180px;
  max-width: 280px;
  padding: 12px 16px 11px;
  border-radius: 18px 18px 10px 10px;
  border: 1px solid var(--surface-border);
  background: rgba(255, 255, 255, 0.88);
  color: var(--text-muted);
  text-align: left;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}
.device-tab:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(15, 23, 42, 0.08);
}
.device-tab--active {
  color: #0f172a;
  background: linear-gradient(180deg, rgba(255, 255, 255, 1), rgba(239, 246, 255, 0.96));
  border-color: rgba(37, 89, 189, 0.24);
  box-shadow: 0 16px 32px rgba(37, 89, 189, 0.12);
}
.device-tab--active::after {
  content: '';
  position: absolute;
  inset: auto 14px -1px 14px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2559bd, #60a5fa);
}
.device-tab__label {
  display: block;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 4px;
  opacity: 0.88;
}
.device-tab__value {
  display: block;
  font-size: 0.9rem;
  font-weight: 800;
  line-height: 1.35;
  word-break: break-word;
}

:global(.dark-mode) .device-tabs-shell {
  background: var(--surface-card-soft) !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .device-tabs-title {
  color: #f8fafc !important;
}

:global(.dark-mode) .device-tab {
  background: rgba(2, 6, 23, 0.96) !important;
  color: #cbd5e1 !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .device-tab--active {
  color: #f8fafc !important;
  background: linear-gradient(180deg, rgba(15, 23, 42, 1), rgba(30, 41, 59, 0.94)) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(320px, 0.9fr);
  gap: 22px;
  align-items: start;
}
.main-column, .side-column { display: flex; flex-direction: column; gap: 18px; }
.panel {
  background: var(--surface-panel-strong);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  box-shadow: 0 18px 40px var(--surface-shadow);
}

:global(.dark-mode) .chart-panel {
  background: transparent;
}

:global(.dark-mode) .side-panel {
  background: var(--surface-card-soft) !important;
}

:global(.dark-mode) .side-panel .panel-title,
:global(.dark-mode) .side-panel .panel-eyebrow,
:global(.dark-mode) .side-panel .info-row span,
:global(.dark-mode) .side-panel .alert-meta,
:global(.dark-mode) .side-panel .empty-state,
:global(.dark-mode) .side-panel .alert-item p {
  color: #e2e8f0 !important;
}

:global(.dark-mode) .side-panel .info-row strong,
:global(.dark-mode) .side-panel .status-card strong,
:global(.dark-mode) .side-panel .alert-item strong {
  color: #f8fafc !important;
}
.chart-panel {
  padding: 0;
  border: none;
  background: transparent;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}
.panel-header.compact { margin-bottom: 14px; }
.panel-eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 800;
  color: #2559bd;
}
.panel-title { margin: 0; font-size: 1.12rem; font-weight: 800; color: var(--text-main); }
.panel-subtitle { margin: 6px 0 0; color: var(--text-muted); font-size: 0.92rem; }
.panel-live {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.1);
  color: #047857;
  font-size: 0.8rem;
  font-weight: 800;
  white-space: nowrap;
}
.side-panel { padding: 22px; }
.info-list, .alert-list { display: grid; gap: 12px; }
.info-row, .status-card, .alert-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--surface-panel-strong);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

:global(.dark-mode) .info-row,
:global(.dark-mode) .status-card,
:global(.dark-mode) .alert-item {
  background: var(--surface-card) !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .side-panel .info-row,
:global(.dark-mode) .side-panel .status-card,
:global(.dark-mode) .side-panel .alert-item {
  background: rgba(2, 6, 23, 0.98) !important;
  border-color: var(--surface-border) !important;
  background-image: none !important;
}
.info-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.info-row span { color: var(--text-muted); font-size: 0.82rem; font-weight: 700; }
.state-on { color: #047857; }
.state-off { color: #b45309; }
.alert-item p {
  margin: 10px 0 8px;
  color: var(--text-main);
  font-size: 0.92rem;
  line-height: 1.5;
}
.alert-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.alert-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.alert-open { background: rgba(239, 68, 68, 0.12); color: #b91c1c; }
.alert-read { background: rgba(37, 89, 189, 0.12); color: #2559bd; }
.alert-meta { font-size: 0.8rem; color: var(--text-muted); }
.empty-state { margin: 0; color: var(--text-muted); font-size: 0.92rem; }
.status-grid { display: grid; gap: 12px; }
.status-card strong { display: block; margin-top: 4px; }

:global(.dark-mode) .chart-frame {
  background: var(--surface-plot) !important;
  border-color: rgba(51, 65, 85, 0.76) !important;
}

:global(.dark-mode) .chart-frame :deep(canvas),
:global(.dark-mode) .chart-frame :deep(svg) {
  filter: brightness(0.98) contrast(1.02);
}

@media (max-width: 1100px) {
  .hero-panel, .dashboard-grid { grid-template-columns: 1fr; }
  .hero-panel { flex-direction: column; }
  .hero-summary { flex: 1 1 auto; grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 768px) {
  .hero-panel, .chart-panel, .side-panel { padding: 18px; }
  .hero-summary { grid-template-columns: 1fr; }
  .panel-header { flex-direction: column; }
  .device-tabs-shell { padding: 16px; }
  .device-tab { min-width: 160px; }
}
</style>
