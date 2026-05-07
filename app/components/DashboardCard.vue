<template>
  <article class="metric-card" :class="[metricToneClass, { 'card-alert': isAlert, 'is-empty': type === 'presence' && mainText === 'Empty', 'metric-card--loading': isLoading }]">
    <div class="metric-card-top">
      <div class="metric-title-group">
        <div class="metric-icon">{{ metricMeta.code }}</div>
        <span v-if="!isLoading" class="metric-title">{{ title }}</span>
        <span v-else class="metric-skeleton metric-skeleton--title" aria-hidden="true"></span>
      </div>
      <span v-if="!isLoading" class="metric-chip">{{ metricMeta.unit }}</span>
      <span v-else class="metric-skeleton metric-skeleton--chip" aria-hidden="true"></span>
    </div>

    <p v-if="subtitle && !isLoading" class="card-subtitle">{{ subtitle }}</p>
    <span v-else-if="isLoading" class="metric-skeleton metric-skeleton--subtitle" aria-hidden="true"></span>
    <div v-if="!isLoading" class="card-value" :class="valueClass">{{ mainText }}</div>
    <span v-else class="metric-skeleton metric-skeleton--value" aria-hidden="true"></span>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  mainText: { type: String, default: '' },
  description: { type: String, default: '' },
  isAlert: { type: Boolean, default: false },
  type: { type: String, default: '' },
  isLoading: { type: Boolean, default: false }
})

const metricMeta = computed(() => {
  if (props.type === 'hr') return { code: 'HR', unit: 'BPM' }
  if (props.type === 'hrv') return { code: 'HRV', unit: 'MS' }
  if (props.type === 'resp') return { code: 'RESP', unit: 'RPM' }
  if (props.type === 'presence') return { code: 'BED', unit: 'STATE' }
  return { code: '--', unit: '' }
})

const metricToneClass = computed(() => {
  if (props.type === 'hr') return 'type-hr'
  if (props.type === 'hrv') return 'type-hrv'
  if (props.type === 'resp') return 'type-resp'
  if (props.type === 'presence') return 'type-presence'
  return ''
})

const valueClass = computed(() => {
  if (props.type === 'hr') return 'heart-color'
  if (props.type === 'hrv') return 'hrv-color'
  if (props.type === 'resp') return 'resp-color'
  if (props.type === 'presence') return 'presence-color'
  return ''
})
</script>

<style scoped>
.metric-card {
  position: relative;
  overflow: hidden;
  padding: 22px 22px 20px;
  border-radius: 24px;
  background: var(--surface-panel-strong);
  border: 1px solid var(--surface-border);
  box-shadow: 0 14px 34px var(--surface-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.metric-card--loading {
  opacity: 0.92;
}

:global(.dark-mode) .metric-card {
  background: var(--surface-panel-strong) !important;
  border-color: var(--surface-border) !important;
  box-shadow: 0 18px 40px var(--surface-shadow) !important;
}

:global(.dark-mode) .metric-card:hover {
  box-shadow: 0 20px 44px rgba(2, 6, 23, 0.42) !important;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}
.metric-card::after {
  content: '';
  position: absolute;
  inset: auto -18% -38% auto;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 89, 189, 0.08), transparent 70%);
  pointer-events: none;
}

:global(.dark-mode) .metric-card::after {
  background: radial-gradient(circle, rgba(37, 89, 189, 0.12), transparent 70%);
}

:global(.dark-mode) .metric-skeleton {
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.92), rgba(51, 65, 85, 0.96), rgba(30, 41, 59, 0.92));
  background-size: 200% 100%;
}
.metric-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.metric-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}
.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 0.9rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  color: #ffffff;
  background: #2559bd;
  box-shadow: 0 10px 20px rgba(37, 89, 189, 0.2);
}
.metric-title {
  font-size: 1.06rem;
  font-weight: 800;
  color: var(--text-main);
  letter-spacing: -0.02em;
  line-height: 1.1;
}
.metric-chip {
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  color: #2559bd;
  background: rgba(37, 89, 189, 0.08);
}

.metric-skeleton {
  display: inline-block;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(226, 232, 240, 0.9), rgba(241, 245, 249, 1), rgba(226, 232, 240, 0.9));
  background-size: 200% 100%;
  animation: metric-skeleton-shimmer 1.3s ease-in-out infinite;
}

.metric-skeleton--title {
  width: 120px;
  height: 1rem;
}

.metric-skeleton--chip {
  width: 48px;
  height: 1.8rem;
}

.metric-skeleton--subtitle {
  width: 140px;
  height: 0.92rem;
  margin-top: 8px;
}

.metric-skeleton--value {
  width: 62%;
  height: 2.4rem;
  margin-top: 10px;
  border-radius: 18px;
}
.type-hr .metric-icon { background: linear-gradient(135deg, #ef4444, #f97316); }
.type-hrv .metric-icon { background: linear-gradient(135deg, #06b6d4, #0284c7); }
.type-resp .metric-icon { background: linear-gradient(135deg, #8b5cf6, #6366f1); }
.type-presence .metric-icon { background: linear-gradient(135deg, #10b981, #14b8a6); }
.type-hr .metric-chip { color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.type-hrv .metric-chip { color: #0891b2; background: rgba(6, 182, 212, 0.08); }
.type-resp .metric-chip { color: #7c3aed; background: rgba(139, 92, 246, 0.08); }
.type-presence .metric-chip { color: #059669; background: rgba(16, 185, 129, 0.08); }
.card-subtitle {
  margin: 8px 0 0;
  font-size: 0.92rem;
  line-height: 1.3;
  color: #64748b;
  font-weight: 700;
}

.card-subtitle {
  color: var(--text-main);
}

:global(.dark-mode) .metric-title {
  color: #f8fafc !important;
}

:global(.dark-mode) .card-subtitle {
  color: #e2e8f0 !important;
}
.card-value {
  margin: 2px 0 16px;
  font-size: clamp(1.9rem, 2.6vw, 2.4rem);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
}

@keyframes metric-skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}
.heart-color { color: #ef4444; }
.hrv-color { color: #0891b2; }
.resp-color { color: #7c3aed; }
.presence-color { color: #059669; }
.metric-footer { display: flex; align-items: center; justify-content: flex-start; }
.card-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 800;
}
.status-ok { color: #166534; background: #dcfce7; }
.status-error { color: #991b1b; background: #fee2e2; }

:global(.dark-mode) .status-ok {
  color: #a7f3d0 !important;
  background: rgba(16, 185, 129, 0.16) !important;
}

:global(.dark-mode) .status-error {
  color: #fecaca !important;
  background: rgba(239, 68, 68, 0.16) !important;
}
.card-alert {
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 0 18px 40px rgba(239, 68, 68, 0.08);
}

:global(.dark-mode) .card-alert {
  border-color: rgba(248, 113, 113, 0.28) !important;
  box-shadow: 0 18px 40px rgba(239, 68, 68, 0.12) !important;
}
.is-empty {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.98), rgba(241, 245, 249, 0.95));
}

:global(.dark-mode) .is-empty {
  background: var(--surface-panel-strong) !important;
  border-color: var(--surface-border) !important;
  box-shadow: 0 18px 40px var(--surface-shadow) !important;
}
.is-empty .presence-color { color: #64748b !important; }

:global(.dark-mode) .is-empty .presence-color {
  color: #94a3b8 !important;
}

@media (max-width: 640px) {
  .metric-card { padding: 18px; border-radius: 20px; }
}
</style>
