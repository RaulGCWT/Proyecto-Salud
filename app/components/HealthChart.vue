<template>
  <div class="chart-container" :class="{ 'border-alert': isCurrentValueAlert }">
    <div class="chart-controls">
      <button 
        v-for="m in metrics" :key="m.id"
        :class="['control-btn', { active: activeMetric === m.id }]"
        @click="activeMetric = m.id"
      >
        {{ m.name }}
        <span v-if="getAlertStatus(m.id)" class="alert-dot"></span>
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

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, VisualMapComponent])

const health = useHealthStore()
const activeMetric = ref('hr')

const metrics = [
  { id: 'hr', name: 'Heart Rate', color: '#ef4444', min: 50, max: 100 },
  { id: 'hrv', name: 'HR Variability', color: '#06b6d4', min: 20, max: 100 },
  { id: 'resp', name: 'Resp. Rate', color: '#8b5cf6', min: 10, max: 20 }
]

const getAlertStatus = (id) => health.alertHistory.some(a => a.sensor.toLowerCase().includes(id))
const isCurrentValueAlert = computed(() => getAlertStatus(activeMetric.value))

const currentData = computed(() => {
  if (activeMetric.value === 'hrv') return health.hrvHistory
  if (activeMetric.value === 'resp') return health.respHistory
  return health.hrHistory
})

const currentColor = computed(() => metrics.find(m => m.id === activeMetric.value).color)

const chartOption = computed(() => {
  const metricConfig = metrics.find(m => m.id === activeMetric.value)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category', boundaryGap: false,
      data: currentData.value.map(d => d.time),
      axisLine: { lineStyle: { color: '#cbd5e1' } }
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    visualMap: {
      show: false,
      pieces: [
        { gt: metricConfig.min, lte: metricConfig.max, color: currentColor.value },
        { gt: metricConfig.max, color: '#000' },
        { lte: metricConfig.min, color: '#ff0000' }
      ]
    },
    series: [{
      name: metricConfig.name, type: 'line', data: currentData.value.map(d => d.value),
      smooth: true, showSymbol: isCurrentValueAlert.value, symbolSize: 10, lineStyle: { width: 4 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: `${currentColor.value}44` }, { offset: 1, color: `${currentColor.value}00` }]
        }
      }
    }]
  }
})
</script>

<style scoped>
.chart-container { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 450px; margin-top: 32px; border: 2px solid transparent; transition: all 0.3s; }
.border-alert { border-color: #ef4444; animation: blink-border 1.5s infinite; }
@keyframes blink-border { 50% { border-color: transparent; } }
.chart-controls { display: flex; gap: 12px; margin-bottom: 20px; }
.control-btn { padding: 8px 16px; border-radius: 8px; border: 1px solid #e2e8f0; background: white; color: #64748b; font-weight: 600; cursor: pointer; position: relative; }
.control-btn.active { background: #0f172a; color: white; }
.alert-dot { position: absolute; top: -4px; right: -4px; width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 2px solid white; }
.chart { height: 320px; width: 100%; }
</style>