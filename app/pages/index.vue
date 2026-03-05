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

const health = useHealthStore()
const rulesStore = useRulesStore()

// Función auxiliar para comprobar si el valor actual rompe alguna regla
const checkCurrentValue = (variable, currentVal) => {
  return rulesStore.rules.some(rule => {
    if (rule.variable !== variable) return false
    return rule.operator === '>' ? currentVal > rule.value : currentVal < rule.value
  })
}

const isHRAlert = computed(() => checkCurrentValue('hr', health.heartRate))
const isHRVAlert = computed(() => checkCurrentValue('hrv', health.hrv))
const isRespAlert = computed(() => checkCurrentValue('resp', health.respiratoryRate))
</script>

<style scoped>
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.analytics-section { margin-top: 48px; }
.section-title { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin-bottom: 16px; font-family: 'Inter', sans-serif; }
</style>