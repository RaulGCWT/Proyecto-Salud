<template>
  <article class="metric-card" :class="[metricToneClass, { 'card-alert': isAlert, 'is-empty': type === 'presence' && mainText === 'Empty' }]">
    <div class="metric-card-top">
      <div class="metric-icon">{{ metricMeta.code }}</div>
      <span class="metric-chip">{{ metricMeta.unit }}</span>
    </div>

    <span class="card-label">{{ title }}</span>
    <div class="card-value" :class="valueClass">{{ mainText }}</div>

    <div class="metric-footer">
      <span class="card-indicator" :class="isAlert ? 'status-error' : 'status-ok'">
        {{ description }}
      </span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  mainText: { type: String, default: '' },
  description: { type: String, default: '' },
  isAlert: { type: Boolean, default: false },
  type: { type: String, default: '' }
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
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95));
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
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
.metric-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
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
.metric-chip {
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  color: #2559bd;
  background: rgba(37, 89, 189, 0.08);
}
.type-hr .metric-icon { background: linear-gradient(135deg, #ef4444, #f97316); }
.type-hrv .metric-icon { background: linear-gradient(135deg, #06b6d4, #0284c7); }
.type-resp .metric-icon { background: linear-gradient(135deg, #8b5cf6, #6366f1); }
.type-presence .metric-icon { background: linear-gradient(135deg, #10b981, #14b8a6); }
.type-hr .metric-chip { color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.type-hrv .metric-chip { color: #0891b2; background: rgba(6, 182, 212, 0.08); }
.type-resp .metric-chip { color: #7c3aed; background: rgba(139, 92, 246, 0.08); }
.type-presence .metric-chip { color: #059669; background: rgba(16, 185, 129, 0.08); }
.card-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748b;
}
.card-value {
  margin: 10px 0 16px;
  font-size: clamp(1.9rem, 2.6vw, 2.4rem);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
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
.card-alert {
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 0 18px 40px rgba(239, 68, 68, 0.08);
}
.is-empty {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.98), rgba(241, 245, 249, 0.95));
}
.is-empty .presence-color { color: #64748b !important; }

@media (max-width: 640px) {
  .metric-card { padding: 18px; border-radius: 20px; }
}
</style>
