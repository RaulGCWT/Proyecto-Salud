<template>
  <article class="overview-card" :class="[`overview-card--${card.status}`]">
    <div class="overview-card__header">
      <div class="overview-card__identity">
        <p class="overview-card__eyebrow">Mac: {{ card.mac }}</p>
        <h3 class="overview-card__title">{{ card.deviceName }}</h3>
        <p class="overview-card__subtitle">{{ card.residentName }}</p>
      </div>

      <span class="overview-card__badge">{{ badgeLabel }}</span>
    </div>

    <div class="overview-card__metrics">
      <div class="metric-box">
        <span class="metric-box__label">HR</span>
        <strong class="metric-box__value">{{ card.heartRate || '--' }} <small>BPM</small></strong>
      </div>

      <div class="metric-box">
        <span class="metric-box__label">HRV</span>
        <strong class="metric-box__value">{{ card.hrv || '--' }} <small>MS</small></strong>
      </div>

      <div class="metric-box">
        <span class="metric-box__label">RR</span>
        <strong class="metric-box__value">{{ card.respiratoryRate || '--' }} <small>BR/M</small></strong>
      </div>
    </div>

    <div class="overview-card__sparkline" aria-hidden="true">
      <svg viewBox="0 0 100 24" preserveAspectRatio="none">
        <path v-if="card.sparklinePaths?.heartRate" :d="card.sparklinePaths.heartRate" class="sparkline-path sparkline-path--heart" />
        <path v-if="card.sparklinePaths?.respiratoryRate" :d="card.sparklinePaths.respiratoryRate" class="sparkline-path sparkline-path--resp" />
        <path v-if="card.sparklinePaths?.hrv" :d="card.sparklinePaths.hrv" class="sparkline-path sparkline-path--hrv" />
      </svg>
    </div>

    <div class="overview-card__legend" aria-hidden="true">
      <span class="legend-chip">
        <span class="legend-dot legend-dot--heart"></span>
        HR
      </span>
      <span class="legend-chip">
        <span class="legend-dot legend-dot--resp"></span>
        RESP
      </span>
      <span class="legend-chip">
        <span class="legend-dot legend-dot--hrv"></span>
        HRV
      </span>
    </div>

    <div class="overview-card__meta">
      <span>{{ card.isOccupied ? 'Occupied' : 'Empty' }}</span>
      <span>{{ card.lastSeenLabel }}</span>
    </div>

    <div class="overview-card__alert">
      <span class="overview-card__alert-label">Active Alerts:</span>
      <p class="overview-card__alert-text">{{ card.latestAlertMessage || 'none' }}</p>
    </div>

    <button class="overview-card__action" type="button" @click="$emit('view-details', card)">
      View Details
    </button>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    required: true
  }
})

defineEmits(['view-details'])

const badgeLabel = computed(() => {
  if (props.card.status === 'urgent') return 'Urgent'
  if (props.card.status === 'attention') return 'Attention'
  if (props.card.status === 'connected') return 'Connected'
  if (props.card.status === 'offline') return 'Offline'
  return 'Stable'
})
</script>

<style scoped>
.overview-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px;
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94));
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.05);
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 46px rgba(15, 23, 42, 0.08);
}

.overview-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.overview-card__eyebrow {
  margin: 0 0 6px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.overview-card__title {
  margin: 0;
  font-size: 1.36rem;
  line-height: 1.15;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: var(--text-main);
}

.overview-card__subtitle {
  margin: 8px 0 0;
  font-size: 0.88rem;
  color: var(--text-muted);
  font-weight: 700;
}

.overview-card__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.overview-card__metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-box {
  padding: 14px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.metric-box__label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.metric-box__value {
  font-size: 1.9rem;
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.metric-box__value small {
  font-size: 0.72rem;
  font-weight: 800;
}

.overview-card__sparkline {
  height: 70px;
}

.overview-card__sparkline svg {
  width: 100%;
  height: 100%;
}

.overview-card__sparkline path {
  fill: none;
  vector-effect: non-scaling-stroke;
}

.sparkline-path {
  stroke-width: 1.9;
  opacity: 0.95;
}

.sparkline-path--heart {
  stroke: #2563eb;
}

.sparkline-path--resp {
  stroke: #0f9d9d;
}

.sparkline-path--hrv {
  stroke: #f97316;
}

.overview-card__legend {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: -6px;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.legend-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.legend-dot--heart {
  background: #2563eb;
}

.legend-dot--resp {
  background: #0f9d9d;
}

.legend-dot--hrv {
  background: #f97316;
}

.overview-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--text-muted);
}

.overview-card__alert {
  display: flex;
  align-items: baseline;
  gap: 6px;
  flex-wrap: wrap;
  margin: -4px 0 0;
}

.overview-card__alert-label {
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
  line-height: 1.4;
}

.overview-card__alert-text {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.45;
  font-weight: 700;
  color: var(--text-main);
}

.overview-card__action {
  width: 100%;
  padding: 13px 16px;
  border: 0;
  border-radius: 18px;
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  background: rgba(226, 232, 240, 0.9);
  color: #0f172a;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.overview-card__action:hover {
  transform: translateY(-1px);
}

.overview-card--stable {
  border-color: rgba(16, 185, 129, 0.18);
}

.overview-card--stable .overview-card__badge {
  background: rgba(144, 239, 239, 0.8);
  color: #006a6a;
}

.overview-card--connected {
  border-color: rgba(37, 99, 235, 0.16);
}

.overview-card--connected .overview-card__badge {
  background: rgba(219, 234, 254, 0.95);
  color: #1d4ed8;
}

.overview-card--attention {
  border-color: rgba(159, 0, 15, 0.14);
}

.overview-card--attention .overview-card__badge {
  background: rgba(255, 218, 214, 0.9);
  color: #93000d;
}

.overview-card--urgent {
  border-color: rgba(186, 26, 26, 0.24);
  box-shadow: 0 20px 42px rgba(186, 26, 26, 0.1);
}

.overview-card--urgent .overview-card__badge {
  background: rgba(255, 218, 214, 1);
  color: #ba1a1a;
}

.overview-card--urgent .overview-card__action {
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  color: #ffffff;
}

.overview-card--offline {
  border-color: rgba(115, 119, 132, 0.22);
}

.overview-card--offline .overview-card__badge {
  background: rgba(224, 227, 229, 0.9);
  color: #434653;
}

.overview-card--offline .sparkline-path {
  opacity: 0.65;
}

:global(.dark-mode) .overview-card {
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.95)) !important;
  border-color: var(--surface-border) !important;
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.3) !important;
}

:global(.dark-mode) .metric-box {
  background: rgba(2, 6, 23, 0.92) !important;
  border-color: rgba(51, 65, 85, 0.76) !important;
}

:global(.dark-mode) .overview-card__title,
:global(.dark-mode) .metric-box__value,
:global(.dark-mode) .overview-card__alert-text {
  color: #f8fafc !important;
}

:global(.dark-mode) .overview-card__subtitle,
:global(.dark-mode) .overview-card__eyebrow,
:global(.dark-mode) .overview-card__meta,
:global(.dark-mode) .metric-box__label,
:global(.dark-mode) .legend-chip,
:global(.dark-mode) .overview-card__alert-label {
  color: #94a3b8 !important;
}

:global(.dark-mode) .overview-card__action {
  background: rgba(15, 23, 42, 0.98) !important;
  color: #f8fafc !important;
  border: 1px solid rgba(51, 65, 85, 0.76);
}

:global(.dark-mode) .overview-card--urgent .overview-card__action {
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%) !important;
  border-color: transparent !important;
}

@media (max-width: 768px) {
  .overview-card {
    padding: 18px;
    border-radius: 24px;
  }

  .overview-card__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
