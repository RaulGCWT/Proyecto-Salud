const resolveMetricConfig = (activeMetric, metrics) => metrics.find(metric => metric.id === activeMetric) || metrics[0]

const buildVisualMapPieces = (rules, metricColor) => {
  const pieces = []
  const maxRule = rules.find(rule => rule.operator === '>')
  const minRule = rules.find(rule => rule.operator === '<')

  // Pintamos primero los rangos extremos para que ECharts aplique bien los colores.
  if (minRule) {
    pieces.push({ lte: minRule.value, color: '#4b5563' })
  }

  if (maxRule) {
    pieces.push({ gt: maxRule.value, color: '#000000' })
  }

  const normalMin = minRule ? minRule.value : -1
  const normalMax = maxRule ? maxRule.value : 999
  pieces.push({ gt: normalMin, lte: normalMax, color: metricColor })

  return pieces
}

export const buildHealthChartOption = ({ activeMetric, metrics, currentData, rules, isCurrentValueAlert }) => {
  const metricConfig = resolveMetricConfig(activeMetric, metrics)
  const filteredRules = rules.filter(rule => rule.variable === activeMetric)
  const pieces = buildVisualMapPieces(filteredRules, metricConfig.color)

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.96)',
      borderColor: 'rgba(37, 89, 189, 0.18)',
      textStyle: { color: '#ffffff' },
      axisPointer: {
        type: 'line',
        lineStyle: { color: metricConfig.color, width: 2, type: 'dashed' }
      }
    },
    grid: { left: '2%', right: '3%', bottom: '4%', top: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: currentData.map(item => item.time),
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisTick: { show: false },
      axisLabel: { color: '#64748b', fontWeight: 600 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', fontWeight: 600 },
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    visualMap: {
      show: false,
      pieces,
      outOfRange: { color: metricConfig.color }
    },
    series: [{
      name: metricConfig.name,
      type: 'line',
      data: currentData.map(item => item.value),
      smooth: true,
      showSymbol: isCurrentValueAlert,
      symbolSize: 10,
      lineStyle: { width: 4, color: metricConfig.color },
      itemStyle: { color: metricConfig.color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: `${metricConfig.color}44` },
            { offset: 1, color: `${metricConfig.color}00` }
          ]
        }
      },
      emphasis: {
        focus: 'series',
        itemStyle: { borderWidth: 2, borderColor: '#ffffff' }
      }
    }]
  }
}
