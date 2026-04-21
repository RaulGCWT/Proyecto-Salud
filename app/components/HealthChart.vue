<template>
  <div class="chart-container" :class="{ 'border-alert': isCurrentValueAlert }">
    <div class="chart-controls">
      <button
        v-for="metric in metrics"
        :key="metric.id"
        :class="['control-btn', { active: activeMetric === metric.id }]"
        @click="activeMetric = metric.id"
      >
        {{ metric.name }}
        <span v-if="getAlertStatus(metric.id)" class="alert-dot"></span>
      </button>
    </div>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'
import { buildHealthChartOption } from '~/utils/healthChart'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, VisualMapComponent])

const health = useHealthStore()
const rulesStore = useRulesStore()
const activeMetric = ref('hr')

const metrics = [
  { id: 'hr', name: 'Heart Rate', color: '#ef4444' },
  { id: 'hrv', name: 'HR Variability', color: '#06b6d4' },
  { id: 'resp', name: 'Resp. Rate', color: '#8b5cf6' }
]

const getAlertStatus = (id) => health.alertHistory.some(alert => alert.sensor.toLowerCase().includes(id))
const isCurrentValueAlert = computed(() => getAlertStatus(activeMetric.value))

const currentData = computed(() => {
  if (activeMetric.value === 'hrv') return health.hrvHistory
  if (activeMetric.value === 'resp') return health.respHistory
  return health.hrHistory
})

const chartOption = computed(() => buildHealthChartOption({
  activeMetric: activeMetric.value,
  metrics,
  currentData: currentData.value,
  rules: rulesStore.rules,
  isCurrentValueAlert: isCurrentValueAlert.value
}))
</script>

<style scoped>
.chart-container {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  height: 450px;
  margin-top: 32px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.border-alert {
  border-color: #ef4444;
  animation: blink-border 1.5s infinite;
}

@keyframes blink-border {
  50% { border-color: transparent; }
}

.chart-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.control-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  position: relative;
}

.control-btn.active {
  background: #0f172a;
  color: white;
}

.alert-dot {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
}

.chart {
  height: 320px;
  width: 100%;
}
</style>
