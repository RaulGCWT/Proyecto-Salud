<template>
  <div>
    <header class="main-header">
      <h1>Live Sensor Monitoring</h1>
      <p>Real-time status of smart mattresses</p>
    </header>

    <section class="sensor-grid">
      <DashboardCard type="hr" title="Heart Rate" :main-text="`${heartRate} BPM`" :is-alert="isHRAlert" :description="isHRAlert ? 'Abnormal HR' : 'Normal'" />
      <DashboardCard type="hrv" title="HR Variability" :main-text="`${hrv} ms`" :is-alert="isHRVAlert" :description="isHRVAlert ? 'High Stress' : 'Normal'" />
      <DashboardCard type="resp" title="Resp. Rate" :main-text="`${respiratoryRate} RPM`" :is-alert="isRespAlert" :description="isRespAlert ? 'Abnormal' : 'Normal'" />
      <DashboardCard type="presence" title="Bed Status" :main-text="isOccupied ? 'In Use' : 'Empty'" :is-alert="false" description="Occupancy" />
    </section>
  </div>
</template>

<script setup>
const { heartRate, respiratoryRate, hrv, isOccupied, isHRAlert, isRespAlert, isHRVAlert } = useHealth()
</script>

<style scoped>
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
</style>