<template>
  <div class="chart-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { computed } from 'vue'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const { hrHistory } = useHealth()

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#0f172a',
    textStyle: { color: '#fff' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: hrHistory.value.map(d => d.time),
    axisLine: { lineStyle: { color: '#cbd5e1' } }
  },
  yAxis: {
    type: 'value',
    min: 40,
    max: 130,
    splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
  },
  series: [{
    name: 'Heart Rate',
    type: 'line',
    data: hrHistory.value.map(d => d.value),
    smooth: true,
    showSymbol: false,
    lineStyle: { color: '#ef4444', width: 3 },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(239, 68, 68, 0.2)' },
          { offset: 1, color: 'rgba(239, 68, 68, 0)' }
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
  height: 400px;
  margin-top: 32px;
  border: 1px solid #f1f5f9;
}
.chart { height: 100%; width: 100%; }
</style>