const resolveMetricConfig = (activeMetric, metrics) => metrics.find(metric => metric.id === activeMetric) || metrics[0]

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;')

const formatTimestampLabel = (timestamp) => {
  if (!timestamp && timestamp !== 0) return ''

  return new Date(Number(timestamp) * 1000).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const groupReadingsByTimestamp = (readings) => {
  const buckets = new Map()

  for (const reading of readings) {
    const timestamp = Number(reading?.ts ?? reading?.timestamp ?? 0)
    if (!Number.isFinite(timestamp) || timestamp <= 0) continue

    const numericValue = Number(reading?.value ?? 0)
    const safeValue = Number.isFinite(numericValue) ? numericValue : 0
    const currentBucket = buckets.get(timestamp) || {
      ts: timestamp,
      values: [],
      count: 0
    }

    currentBucket.count += 1
    currentBucket.values.push(safeValue)
    buckets.set(timestamp, currentBucket)
  }

  return Array.from(buckets.values())
    .sort((left, right) => left.ts - right.ts)
    .map(bucket => {
      const total = bucket.values.reduce((accumulator, value) => accumulator + value, 0)
      const average = bucket.values.length ? total / bucket.values.length : 0
      const latestValue = bucket.values.at(-1) ?? 0
      const minValue = bucket.values.length ? Math.min(...bucket.values) : 0
      const maxValue = bucket.values.length ? Math.max(...bucket.values) : 0

      return {
        ts: bucket.ts,
        time: formatTimestampLabel(bucket.ts),
        value: latestValue,
        average,
        min: minValue,
        max: maxValue,
        count: bucket.count
      }
    })
}

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

export const buildHealthChartOption = ({
  activeMetric,
  metrics,
  currentData,
  rules,
  isCurrentValueAlert,
  xAxisMin,
  xAxisMax
}) => {
  const metricConfig = resolveMetricConfig(activeMetric, metrics)
  const filteredRules = rules.filter(rule => rule.variable === activeMetric)
  const pieces = buildVisualMapPieces(filteredRules, metricConfig.color)
  const groupedData = groupReadingsByTimestamp(currentData)
  const seriesData = groupedData.map(point => ({
    value: [point.ts * 1000, point.value],
    count: point.count,
    average: point.average,
    min: point.min,
    max: point.max,
    time: point.time,
    ts: point.ts
  }))

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
      },
      formatter: (params) => {
        const point = Array.isArray(params) ? params[0] : params
        const payload = point?.data || {}
        const timeLabel = payload.time || formatTimestampLabel((Number(point?.axisValue) || 0) / 1000)
        const valueLabel = Array.isArray(point?.value) ? point.value[1] : point?.value
        const hasBatch = Number(payload.count || 0) > 1

        return [
          `<div style="font-weight:800;margin-bottom:6px;">${escapeHtml(timeLabel || 'N/A')}</div>`,
          `<div style="margin-bottom:4px;">Valor: <strong>${escapeHtml(valueLabel)}</strong></div>`,
          hasBatch ? `<div style="margin-bottom:4px;">Lecturas en el mismo instante: <strong>${escapeHtml(payload.count)}</strong></div>` : '',
          hasBatch ? `<div style="opacity:.85;">Promedio: <strong>${escapeHtml(Number(payload.average || 0).toFixed(1))}</strong></div>` : ''
        ].filter(Boolean).join('')
      }
    },
    grid: { left: '2%', right: '3%', bottom: '4%', top: '12%', containLabel: true },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      min: xAxisMin,
      max: xAxisMax,
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#64748b',
        fontWeight: 600,
        formatter: (value) => formatTimestampLabel((Number(value) || 0) / 1000)
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', fontWeight: 600 },
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    visualMap: {
      show: false,
      dimension: 1,
      pieces,
      outOfRange: { color: metricConfig.color }
    },
    series: [{
      name: metricConfig.name,
      type: 'line',
      data: seriesData,
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
