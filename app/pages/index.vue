<template>
  <div class="dashboard-page">
    <section class="hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">Clinical Sentinel</p>
        <h1>Live Monitoring Overview</h1>
        <p class="hero-description">
          Real-time biometrics from <strong>{{ currentDeviceLabel }}</strong> with synchronized telemetry, alert handling and occupancy state.
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
            {{ rulesStore.rules.length }} active rules
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
              <span class="alert-meta">{{ alert.time }} · {{ alert.mac }}</span>
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
              <strong>{{ rulesStore.rules.length }}</strong>
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

const health = useHealthStore()
const rulesStore = useRulesStore()

useHead({
  title: 'Clinical Sentinel | Dashboard'
})

onMounted(async () => {
  await Promise.all([
    rulesStore.fetchRules(),
    health.fetchAlertHistory()
  ])
})

const hasRuleAlert = (variable, currentValue) => {
  const numericValue = Number(currentValue)

  return rulesStore.rules.some((rule) => {
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
  const heartRateAlert = hasRuleAlert('hr', health.heartRate)
  const hrvAlert = hasRuleAlert('hrv', health.hrv)
  const respiratoryAlert = hasRuleAlert('resp', health.respiratoryRate)

  return [
    {
      key: 'hr',
      type: 'hr',
      title: 'Heart Rate',
      mainText: `${health.heartRate} BPM`,
      isAlert: heartRateAlert,
      description: heartRateAlert ? 'Abnormal HR' : 'Normal range'
    },
    {
      key: 'hrv',
      type: 'hrv',
      title: 'HR Variability',
      mainText: `${health.hrv} ms`,
      isAlert: hrvAlert,
      description: hrvAlert ? 'High stress pattern' : 'Stable trend'
    },
    {
      key: 'resp',
      type: 'resp',
      title: 'Resp. Rate',
      mainText: `${health.respiratoryRate} RPM`,
      isAlert: respiratoryAlert,
      description: respiratoryAlert ? 'Abnormal breathing' : 'Normal range'
    },
    {
      key: 'presence',
      type: 'presence',
      title: 'Bed Status',
      mainText: health.isOccupied ? 'In Use' : 'Empty',
      isAlert: false,
      description: 'Occupancy'
    }
  ]
})

const recentAlerts = computed(() => health.alertHistory.slice(0, 4))
const openAlerts = computed(() => recentAlerts.value.filter(alert => alert.status !== 'READ'))
const latestAlert = computed(() => health.alertHistory[0] || null)
const currentDeviceLabel = computed(() => health.currentDeviceId !== 'N/A' ? health.currentDeviceId : health.currentMac)
const hasLiveData = computed(() => health.latestReadings.length > 0 || health.heartRate > 0 || health.hrv > 0 || health.respiratoryRate > 0)
</script>

<style scoped>
.dashboard-page { display: flex; flex-direction: column; gap: 24px; }
.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(37, 89, 189, 0.08), rgba(255, 255, 255, 0.96));
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
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
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(10px);
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
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(320px, 0.9fr);
  gap: 22px;
  align-items: start;
}
.main-column, .side-column { display: flex; flex-direction: column; gap: 18px; }
.panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.04);
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
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.14);
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

@media (max-width: 1100px) {
  .hero-panel, .dashboard-grid { grid-template-columns: 1fr; }
  .hero-panel { flex-direction: column; }
  .hero-summary { flex: 1 1 auto; grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 768px) {
  .hero-panel, .chart-panel, .side-panel { padding: 18px; }
  .hero-summary { grid-template-columns: 1fr; }
  .panel-header { flex-direction: column; }
}
</style>
