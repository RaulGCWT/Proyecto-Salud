<template>
  <div>
    <header class="main-header">
      <h1>Live Sensor Monitoring</h1>
      <p>Real-time status of smart mattresses</p>
    </header>

    <section class="sensor-grid">
      <DashboardCard 
        type="hr" 
        title="Heart Rate" 
        :main-text="`${health.heartRate} BPM`" 
        :is-alert="isHRAlert" 
        :description="isHRAlert ? 'Abnormal HR' : 'Normal'" 
      />
      <DashboardCard 
        type="hrv" 
        title="HR Variability" 
        :main-text="`${health.hrv} ms`" 
        :is-alert="isHRVAlert" 
        :description="isHRVAlert ? 'High Stress' : 'Normal'" 
      />
      <DashboardCard 
        type="resp" 
        title="Resp. Rate" 
        :main-text="`${health.respiratoryRate} RPM`" 
        :is-alert="isRespAlert" 
        :description="isRespAlert ? 'Abnormal' : 'Normal'" 
      />
      <DashboardCard 
        type="presence" 
        title="Bed Status" 
        :main-text="health.isOccupied ? 'In Use' : 'Empty'" 
        :is-alert="false" 
        description="Occupancy" 
      />
    </section>

    <section class="analytics-section">
      <h3 class="section-title">Heart Rate Vitality Trend</h3>
      <HealthChart />
    </section>
  </div>
</template>

<script setup>
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { computed, onMounted } from 'vue'

const health = useHealthStore()
const rulesStore = useRulesStore()

// Cargamos las reglas de la base de datos al montar el dashboard
onMounted(async () => {
  await rulesStore.fetchRules()
})

// FunciÃ³n auxiliar para comprobar si el valor actual rompe alguna regla
const checkCurrentValue = (variable, currentVal) => {
  if (!rulesStore.rules) return false
  return rulesStore.rules.some(rule => {
    if (rule.variable !== variable) return false
    const val = Number(currentVal)
    const threshold = Number(rule.value)
    return rule.operator === '>' ? val > threshold : val < threshold
  })
}

const isHRAlert = computed(() => checkCurrentValue('hr', health.heartRate))
const isHRVAlert = computed(() => checkCurrentValue('hrv', health.hrv))
const isRespAlert = computed(() => checkCurrentValue('resp', health.respiratoryRate))
</script>

<style scoped>
.main-header { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
.main-header h1 { margin: 0; font-size: 1.9rem; font-weight: 800; color: var(--text-main); }
.main-header p { margin: 4px 0 0; color: var(--text-muted); }
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.analytics-section { margin-top: 2rem; padding: 1.5rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; }
.section-title { margin: 0 0 1rem; font-size: 1.1rem; font-weight: 700; color: var(--text-main); }
</style>
