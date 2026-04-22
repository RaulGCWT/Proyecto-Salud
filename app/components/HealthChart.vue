<template>
  <section class="chart-shell" :class="{ 'chart-alert': isCurrentValueAlert }">
    <div class="chart-header">
      <div class="chart-heading">
        <p class="chart-eyebrow">Telemetry analytics</p>
        <h3 class="chart-title">Vital Biometrics Stream</h3>
        <p class="chart-subtitle">Continuous synchronization of the latest sensor data.</p>
      </div>
    </div>

    <div class="chart-summary">
      <div class="summary-item">
        <span class="summary-label">Active metric</span>
        <strong>{{ activeMetricLabel }}</strong>
      </div>
      <div class="summary-item">
        <span class="summary-label">Latest value</span>
        <strong>{{ latestValueLabel }}</strong>
      </div>
    </div>

    <div class="chart-toolbar">
      <div class="range-controls">
        <button
          v-for="range in timeRanges"
          :key="range.id"
          :class="['control-btn', { active: selectedRange === range.id }]"
          @click="selectedRange = range.id"
        >
          {{ range.label }}
        </button>
      </div>

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
    </div>

    <div class="chart-frame">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>

    <div class="chart-legend">
      <div class="legend-item">
        <span class="legend-dot legend-primary"></span>
        <span>Current stream</span>
      </div>
    </div>
  </section>
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
const selectedRange = ref('1h')

const metrics = [
  { id: 'hr', name: 'Heart Rate', color: '#ef4444' },
  { id: 'hrv', name: 'HR Variability', color: '#06b6d4' },
  { id: 'resp', name: 'Resp. Rate', color: '#8b5cf6' }
]

const timeRanges = [
  { id: '1h', label: '1h', seconds: 60 * 60 },
  { id: '6h', label: '6h', seconds: 6 * 60 * 60 },
  { id: '12h', label: '12h', seconds: 12 * 60 * 60 }
]

const getAlertStatus = (id) => health.alertHistory.some(alert => alert.sensor.toLowerCase().includes(id))
const isCurrentValueAlert = computed(() => getAlertStatus(activeMetric.value))

const currentData = computed(() => {
  if (activeMetric.value === 'hrv') return health.hrvHistory
  if (activeMetric.value === 'resp') return health.respHistory
  return health.hrHistory
})

const visibleData = computed(() => {
  const rangeConfig = timeRanges.find(range => range.id === selectedRange.value) || timeRanges[0]
  const latestTimestamp = currentData.value.at(-1)?.ts

  if (!latestTimestamp || !currentData.value.length) return currentData.value

  const minimumTimestamp = latestTimestamp - rangeConfig.seconds
  const filteredData = currentData.value.filter(item => item.ts >= minimumTimestamp)

  return filteredData.length ? filteredData : currentData.value.slice(-12)
})

const activeMetricLabel = computed(() => {
  return metrics.find(metric => metric.id === activeMetric.value)?.name || 'Heart Rate'
})

const activeMetricUnit = computed(() => {
  const metric = metrics.find(item => item.id === activeMetric.value)
  if (metric?.id === 'hr') return 'BPM'
  if (metric?.id === 'hrv') return 'MS'
  if (metric?.id === 'resp') return 'RPM'
  return ''
})

const latestValueLabel = computed(() => {
  const latestPoint = visibleData.value[visibleData.value.length - 1]
  if (!latestPoint) return 'No data'
  return `${latestPoint.value}${activeMetricUnit.value ? ` ${activeMetricUnit.value}` : ''}`
})

const chartOption = computed(() => buildHealthChartOption({
  activeMetric: activeMetric.value,
  metrics,
  currentData: visibleData.value,
  rules: rulesStore.rules,
  isCurrentValueAlert: isCurrentValueAlert.value
}))
</script>

<style scoped>
.chart-shell {
  position: relative;
  padding: 26px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.96));
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.04);
  overflow: hidden;
}
.chart-shell::after {
  content: '';
  position: absolute;
  inset: auto -10% -28% auto;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 89, 189, 0.08), transparent 68%);
  pointer-events: none;
}
.chart-alert { border-color: rgba(239, 68, 68, 0.28); }
.chart-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 14px;
}
.chart-heading {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.chart-eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 800;
  color: #2559bd;
}
.chart-title { margin: 0; font-size: 1.18rem; font-weight: 900; color: var(--text-main); }
.chart-subtitle { margin: 6px 0 0; color: var(--text-muted); font-size: 0.92rem; }
.chart-live {
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
.chart-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(248, 250, 252, 0.92);
}
.summary-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-muted);
  font-weight: 800;
}
.summary-item strong {
  color: var(--text-main);
  font-size: 1rem;
  font-weight: 900;
}
.live-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.15);
}
.chart-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 14px;
}
.range-controls,
.chart-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.control-btn {
  position: relative;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: #ffffff;
  color: #64748b;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
.control-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06); }
.control-btn.active {
  color: #ffffff;
  border-color: transparent;
  background: linear-gradient(135deg, #0f172a, #2559bd);
  box-shadow: 0 12px 24px rgba(37, 89, 189, 0.18);
}
.alert-dot {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 10px;
  height: 10px;
  background: #ef4444;
  border: 2px solid #ffffff;
  border-radius: 50%;
}
.chart-frame {
  position: relative;
  min-height: 300px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.95)),
    radial-gradient(circle at top left, rgba(37, 89, 189, 0.08), transparent 40%);
  overflow: hidden;
}
.chart {
  height: 100%;
  min-height: 300px;
  width: 100%;
}
.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-top: 14px;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 700;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legend-primary { background: #2559bd; box-shadow: 0 0 0 5px rgba(37, 89, 189, 0.12); }
.legend-secondary { background: rgba(139, 92, 246, 0.45); }

@media (max-width: 768px) {
  .chart-shell { padding: 18px; }
  .chart-header { flex-direction: column; }
  .chart-summary { grid-template-columns: 1fr; }
  .chart-toolbar { flex-direction: column; align-items: stretch; }
  .range-controls, .chart-controls { justify-content: flex-start; }
  .chart-frame, .chart { min-height: 300px; }
}
</style>
