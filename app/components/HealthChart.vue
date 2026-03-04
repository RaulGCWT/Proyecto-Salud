<template>
  <div class="chart-container">
    <div class="chart-controls">
      <button 
        v-for="m in metrics" 
        :key="m.id"
        :class="['control-btn', { active: activeMetric === m.id }]"
        @click="activeMetric = m.id"
      >
        {{ m.name }}
      </button>
    </div>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ref, computed } from 'vue'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const { hrHistory, hrvHistory, respHistory } = useHealth()
const activeMetric = ref('hr')

const metrics = [
  { id: 'hr', name: 'Heart Rate', color: '#ef4444' },
  { id: 'hrv', name: 'HR Variability', color: '#06b6d4' },
  { id: 'resp', name: 'Resp. Rate', color: '#8b5cf6' }
]

const currentMetricData = computed(() => {
  if (activeMetric.value === 'hrv') return hrvHistory.value
  if (activeMetric.value === 'resp') return respHistory.value
  return hrHistory.value
})

const currentColor = computed(() => metrics.find(m => m.id === activeMetric.value).color)

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#0f172a',
    textStyle: { color: '#fff' }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: currentMetricData.value.map(d => d.time),
    axisLine: { lineStyle: { color: '#cbd5e1' } }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
  },
  series: [{
    name: metrics.find(m => m.id === activeMetric.value).name,
    type: 'line',
    data: currentMetricData.value.map(d => d.value),
    smooth: true,
    showSymbol: false,
    lineStyle: { color: currentColor.value, width: 3 },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: `${currentColor.value}33` }, // 33 es 20% de opacidad en hex
          { offset: 1, color: `${currentColor.value}00` }
        ]
      }
    }
  }]
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
  border: 1px solid #f1f5f9;
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
  transition: all 0.2s;
}
.control-btn:hover { background: #f8fafc; }
.control-btn.active {
  background: #0f172a;
  color: white;
  border-color: #0f172a;
}
.chart { height: 320px; width: 100%; }
</style>