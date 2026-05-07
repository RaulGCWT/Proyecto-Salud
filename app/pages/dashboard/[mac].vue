<template>
  <div class="detail-page">
    <section class="detail-hero" :class="{ 'detail-hero--loading': isLoading }">
      <div class="detail-hero__copy">
        <p class="detail-hero__eyebrow">Clinical Sentinel</p>
        <h1 v-if="!isLoading">{{ currentTitle }}</h1>
        <div v-else class="skeleton skeleton--title" aria-hidden="true"></div>
        <p class="detail-hero__description">
          <template v-if="!isLoading">
            Detailed view of the selected device with live metrics, active rules, and recent alerts.
          </template>
          <span v-else class="skeleton skeleton--text" aria-hidden="true"></span>
        </p>
      </div>

      <div class="detail-hero__meta">
        <div class="detail-meta-card">
          <span>MAC</span>
          <strong v-if="!isLoading">{{ health.currentMac }}</strong>
          <span v-else class="skeleton skeleton--value" aria-hidden="true"></span>
        </div>
        <div class="detail-meta-card">
          <span>Patient</span>
          <strong v-if="!isLoading">{{ currentPatientLabel }}</strong>
          <span v-else class="skeleton skeleton--value" aria-hidden="true"></span>
        </div>
        <div class="detail-meta-card">
          <span>Status</span>
          <strong v-if="!isLoading">{{ health.isOccupied ? 'Occupied' : 'Empty' }}</strong>
          <span v-else class="skeleton skeleton--value" aria-hidden="true"></span>
        </div>
        <div class="detail-meta-card detail-meta-card--action">
          <span>Real time</span>
          <button
            class="detail-hero__action"
            type="button"
            :disabled="isRealtimePending || realtimeSecondsLeft > 0 || !currentDeviceRecord"
            @click="startRealtimeMode"
          >
            {{ realtimeButtonLabel }}
          </button>
        </div>
      </div>
    </section>

    <section class="detail-metrics" :class="{ 'detail-metrics--loading': isLoading }">
      <DashboardCard
        v-for="card in dashboardCards"
        :key="card.key"
        :type="card.type"
        :title="card.title"
        :subtitle="card.subtitle"
        :main-text="card.mainText"
        :is-alert="card.isAlert"
        :is-loading="isLoading"
      />
    </section>

    <section class="detail-grid">
      <div class="detail-grid__main">
        <HealthChart />
      </div>

      <aside class="detail-grid__side">
        <section class="side-panel">
          <p class="side-panel__eyebrow">Device Context</p>
          <h2 class="side-panel__title">Live device snapshot</h2>

          <div class="side-list">
            <div v-for="row in sidePanelRows" :key="row.key" class="side-row">
              <span>{{ row.label }}</span>
              <strong
                v-if="!isLoading"
                :class="['side-row__value', `side-row__value--${row.tone || 'neutral'}`]"
              >
                {{ row.value }}
              </strong>
              <span v-else class="skeleton skeleton--row-value" aria-hidden="true"></span>
            </div>
          </div>
        </section>

        <section class="side-panel">
          <p class="side-panel__eyebrow">Recent alerts</p>
          <h2 class="side-panel__title">Alert queue</h2>

          <div v-if="scopedAlerts.length" class="alert-list">
            <article v-for="alert in scopedAlerts" :key="alert.id" class="alert-card">
              <div class="alert-card__top">
                <strong>{{ alert.sensor }}</strong>
                <span class="alert-card__status">{{ alert.status }}</span>
              </div>
              <p>{{ alert.message }}</p>
              <span class="alert-card__meta">{{ alert.time }} · {{ alert.dateLabel }}</span>
            </article>
          </div>

          <p v-else class="empty-copy">No recent alerts for this device.</p>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup>
import DashboardCard from '~/components/DashboardCard.vue'
import HealthChart from '~/components/HealthChart.vue'
import { useDeviceDashboard } from '~/composables/health/useDeviceDashboard'

const route = useRoute()

const {
  health,
  isLoading,
  currentDeviceRecord,
  currentPatientLabel,
  currentTitle,
  scopedAlerts,
  sidePanelRows,
  dashboardCards,
  isRealtimePending,
  realtimeSecondsLeft,
  realtimeButtonLabel,
  startRealtimeMode
} = useDeviceDashboard(route)

useHead({
  title: 'Clinical Sentinel | Device Detail'
})
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(37, 89, 189, 0.08), rgba(255, 255, 255, 0.96));
  border: 1px solid var(--surface-border);
  box-shadow: 0 18px 40px var(--surface-shadow);
}

.detail-hero--loading {
  opacity: 0.92;
}

.detail-hero__eyebrow {
  margin: 0 0 8px;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2559bd;
}

.detail-hero h1 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  line-height: 1.05;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.detail-hero__description {
  margin: 14px 0 0;
  max-width: 640px;
  line-height: 1.6;
  color: var(--text-muted);
}

.detail-hero__meta {
  display: grid;
  gap: 12px;
  min-width: 260px;
}

.detail-meta-card,
.side-panel,
.alert-card {
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  box-shadow: 0 14px 30px var(--surface-shadow);
}

.detail-meta-card {
  padding: 16px 18px;
}

.detail-meta-card--action {
  display: grid;
  gap: 10px;
}

.detail-meta-card span,
.side-panel__eyebrow,
.side-row span,
.alert-card__meta {
  display: block;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.detail-meta-card strong,
.side-row strong,
.side-panel__title,
.alert-card strong,
.alert-card p {
  color: var(--text-main);
}

.detail-hero__action {
  width: 100%;
  padding: 11px 14px;
  border: 0;
  border-radius: 14px;
  font-size: 0.82rem;
  font-weight: 900;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  color: #ffffff;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.detail-hero__action:hover:not(:disabled) {
  transform: translateY(-1px);
}

.detail-hero__action:disabled {
  opacity: 0.72;
  cursor: wait;
}

.detail-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.detail-metrics--loading {
  opacity: 0.88;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(320px, 0.9fr);
  gap: 22px;
}

.detail-grid__side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.skeleton {
  display: inline-block;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(226, 232, 240, 0.9), rgba(241, 245, 249, 1), rgba(226, 232, 240, 0.9));
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.3s ease-in-out infinite;
}

.skeleton--title {
  width: min(680px, 78%);
  height: clamp(2.2rem, 3vw, 3rem);
  border-radius: 18px;
}

.skeleton--text {
  display: block;
  width: min(620px, 92%);
  height: 1rem;
  margin-top: 2px;
}

.skeleton--value {
  width: 70%;
  height: 1.15rem;
  margin-top: 6px;
}

.skeleton--row-value {
  width: 96px;
  height: 0.95rem;
}

.side-panel {
  padding: 22px;
}

.side-panel__eyebrow {
  margin: 0 0 8px;
  color: #2559bd;
}

.side-panel__title {
  margin: 0 0 18px;
  font-size: 1.14rem;
  font-weight: 900;
}

.side-list,
.alert-list {
  display: grid;
  gap: 12px;
}

.side-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--surface-panel);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.side-row__value--ok {
  color: #0f766e;
}

.side-row__value--warn {
  color: #b45309;
}

.side-row__value--danger {
  color: #b91c1c;
}

.alert-card {
  padding: 16px;
}

.alert-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.alert-card__status {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.alert-card p {
  margin: 10px 0 8px;
  line-height: 1.5;
}

.empty-copy {
  margin: 0;
  color: var(--text-muted);
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

:global(.dark-mode) .detail-hero,
:global(.dark-mode) .detail-meta-card,
:global(.dark-mode) .side-panel,
:global(.dark-mode) .alert-card,
:global(.dark-mode) .side-row {
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.95)) !important;
  border-color: var(--surface-border) !important;
}

:global(.dark-mode) .detail-hero h1,
:global(.dark-mode) .detail-hero__description,
:global(.dark-mode) .detail-meta-card strong,
:global(.dark-mode) .side-panel__title,
:global(.dark-mode) .side-row strong,
:global(.dark-mode) .alert-card strong,
:global(.dark-mode) .alert-card p {
  color: #f8fafc !important;
}

:global(.dark-mode) .detail-meta-card span,
:global(.dark-mode) .side-panel__eyebrow,
:global(.dark-mode) .side-row span,
:global(.dark-mode) .alert-card__meta {
  color: #94a3b8 !important;
}

:global(.dark-mode) .skeleton {
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.92), rgba(51, 65, 85, 0.96), rgba(30, 41, 59, 0.92));
  background-size: 200% 100%;
}

:global(.dark-mode) .side-row__value--ok {
  color: #5eead4 !important;
}

:global(.dark-mode) .side-row__value--warn {
  color: #fbbf24 !important;
}

:global(.dark-mode) .side-row__value--danger {
  color: #fca5a5 !important;
}

@media (max-width: 1100px) {
  .detail-hero,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-hero {
    flex-direction: column;
  }

  .detail-hero__meta {
    min-width: 0;
    width: 100%;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .detail-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .detail-hero,
  .side-panel {
    padding: 18px;
  }

  .detail-metrics,
  .detail-hero__meta {
    grid-template-columns: 1fr;
  }
}
</style>
