<template>
  <div>
    <header class="main-header">
      <h1>Live Sensor Monitoring</h1>
    </header>

    <section class="sensor-grid">
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

    <section class="analytics-section">
      <h3 class="section-title">Heart Rate Vitality Trend</h3>
      <HealthChart />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'

const health = useHealthStore()
const rulesStore = useRulesStore()

onMounted(async () => {
  await rulesStore.fetchRules()
})

const hasRuleAlert = (variable, currentValue) => {
  const numericValue = Number(currentValue)

  return rulesStore.rules.some(rule => {
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
      description: heartRateAlert ? 'Abnormal HR' : 'Normal'
    },
    {
      key: 'hrv',
      type: 'hrv',
      title: 'HR Variability',
      mainText: `${health.hrv} ms`,
      isAlert: hrvAlert,
      description: hrvAlert ? 'High Stress' : 'Normal'
    },
    {
      key: 'resp',
      type: 'resp',
      title: 'Resp. Rate',
      mainText: `${health.respiratoryRate} RPM`,
      isAlert: respiratoryAlert,
      description: respiratoryAlert ? 'Abnormal' : 'Normal'
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
</script>

<style scoped>
.main-header { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
.main-header h1 { margin: 0; font-size: 1.9rem; font-weight: 800; color: var(--text-main); }
.main-header p { margin: 4px 0 0; color: var(--text-muted); }
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.analytics-section { margin-top: 2rem; padding: 1.5rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; }
.section-title { margin: 0 0 1rem; font-size: 1.1rem; font-weight: 700; color: var(--text-main); }
</style>
