<template>
  <div class="overview-page">
    <UiPageHeader
      :eyebrow="isFamilyView ? 'Family Portal' : 'Ward Overview'"
      :title="isFamilyView ? 'My Family' : 'Clinical Device Overview'"
      :subtitle="isFamilyView ? 'Monitor the health of your loved ones in real time.' : 'Monitor the full device floor, review active statuses and open the detailed dashboard for each bed.'"
    />

    <section class="overview-stats">
      <article v-for="item in overviewStats" :key="item.key" class="overview-stat" :class="item.tone">
        <div class="overview-stat__top">
          <div class="overview-stat__icon">
            <span class="material-symbols-outlined" aria-hidden="true">{{ item.icon }}</span>
          </div>
          <span class="overview-stat__label">{{ item.label }}</span>
        </div>
        <strong class="overview-stat__value">{{ item.value }}</strong>
        <p class="overview-stat__note">{{ item.note }}</p>
      </article>
    </section>

    <div class="filters-bar">
      <UiSearchInput v-model="searchQuery" placeholder="Search beds or patients..." />
    </div>

    <section class="overview-grid-shell">
      <div class="overview-grid-shell__header">
        <div>
          <p class="overview-grid-shell__eyebrow">Patient Monitoring Grid</p>
          <h2 class="overview-grid-shell__title">{{ visibleDeviceCards.length }} devices in view</h2>
        </div>
      </div>

      <div v-if="visibleDeviceCards.length" class="overview-grid">
        <OverviewDeviceCard
          v-for="card in visibleDeviceCards"
          :key="card.mac"
          :card="card"
          @view-details="openDeviceDetail"
        />
      </div>

      <section v-else class="overview-empty">
        <span class="material-symbols-outlined" aria-hidden="true">monitoring</span>
        <h2>No devices matched this view</h2>
        <p>Try adjusting the search term to bring matching beds back into view.</p>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import OverviewDeviceCard from '~/components/overview/OverviewDeviceCard.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const RESTRICTED_ROLES = new Set(['family', 'resident'])
const isFamilyView = computed(() => RESTRICTED_ROLES.has(auth.user?.role || ''))
import { useDevicesOverview } from '~/composables/health/useDevicesOverview'
import { useHealthStore } from '~/stores/health'
import { useRulesStore } from '~/stores/rules'

const health = useHealthStore()
const rulesStore = useRulesStore()
const {
  searchQuery,
  visibleDeviceCards,
  overviewStats
} = useDevicesOverview()

function openDeviceDetail(card) {
  const targetMac = String(card?.mac || '').trim()
  if (!targetMac) return

  health.setSelectedMac(targetMac)
  navigateTo(`/dashboard/${encodeURIComponent(targetMac)}`)
}

useHead({
  title: 'Clinical Sentinel | Ward Overview'
})

onMounted(async () => {
  await Promise.all([
    rulesStore.fetchRules(),
    health.fetchDeviceInventory(),
    health.fetchAlertHistory()
  ])
})
</script>

<style scoped>
.overview-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 1440px;
  margin: 0 auto;
  padding-bottom: 20px;
}

.overview-topbar {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 18px;
}

.overview-topbar__copy {
  display: flex;
  align-items: flex-end;
  gap: 18px;
  flex-wrap: wrap;
}

.overview-topbar__heading {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.overview-topbar__eyebrow {
  margin: 0 0 8px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2559bd;
}

.overview-topbar h1 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.overview-topbar__subtitle {
  margin: 8px 0 0;
  max-width: 640px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.overview-search {
  position: relative;
  width: min(420px, 100%);
}

.overview-search-row {
  display: flex;
  justify-content: flex-start;
}

.overview-search span {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.overview-search input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  border: 0;
  border-radius: 18px;
  background: rgba(224, 227, 229, 0.8);
  color: var(--text-main);
  outline: none;
  box-sizing: border-box;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.overview-stat {
  padding: 24px;
  border-radius: 26px;
  border: 1px solid rgba(195, 198, 213, 0.24);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 20px rgba(25, 28, 30, 0.04), 0 12px 40px rgba(25, 28, 30, 0.08);
}

.overview-stat__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.overview-stat__icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
}

.overview-stat__label {
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.overview-stat__value {
  display: block;
  font-size: clamp(2rem, 3vw, 2.5rem);
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.overview-stat__note {
  margin: 10px 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.overview-stat--global .overview-stat__icon {
  background: rgba(0, 50, 125, 0.08);
  color: #00327d;
}

.overview-stat--stable .overview-stat__icon {
  background: rgba(144, 239, 239, 0.35);
  color: #006a6a;
}

.overview-stat--attention .overview-stat__icon {
  background: rgba(255, 218, 214, 0.6);
  color: #93000d;
}

.overview-stat--urgent .overview-stat__icon {
  background: rgba(255, 218, 214, 0.8);
  color: #ba1a1a;
}

.overview-stat--stable .overview-stat__value {
  color: #006a6a;
}

.overview-stat--attention .overview-stat__value {
  color: #93000d;
}

.overview-stat--urgent .overview-stat__value {
  color: #ba1a1a;
}

.overview-grid-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.overview-grid-shell__eyebrow {
  margin: 0 0 8px;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.overview-grid-shell__title {
  margin: 0;
  font-size: 1.36rem;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: var(--text-main);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.overview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 320px;
  padding: 24px;
  border-radius: 28px;
  border: 1px dashed rgba(195, 198, 213, 0.5);
  background: rgba(255, 255, 255, 0.88);
  text-align: center;
}

.overview-empty span {
  font-size: 2rem;
  color: #64748b;
}

.overview-empty h2,
.overview-empty p {
  margin: 0;
}

.overview-empty p {
  max-width: 420px;
  color: var(--text-muted);
  line-height: 1.6;
}

:global(.dark-mode) .overview-topbar h1,
:global(.dark-mode) .overview-grid-shell__title,
:global(.dark-mode) .overview-stat__value,
:global(.dark-mode) .overview-empty h2 {
  color: #f8fafc !important;
}

:global(.dark-mode) .overview-topbar__eyebrow {
  color: #60a5fa !important;
}

:global(.dark-mode) .overview-topbar__subtitle {
  color: #94a3b8 !important;
}

:global(.dark-mode) .overview-search input,
:global(.dark-mode) .overview-stat,
:global(.dark-mode) .overview-empty {
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.95)) !important;
  border-color: var(--surface-border) !important;
  color: #f8fafc !important;
}

:global(.dark-mode) .overview-stat__label,
:global(.dark-mode) .overview-stat__note,
:global(.dark-mode) .overview-grid-shell__eyebrow,
:global(.dark-mode) .overview-empty p,
:global(.dark-mode) .overview-search span {
  color: #94a3b8 !important;
}

@media (max-width: 1200px) {
  .overview-stats,
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .overview-topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .overview-stats,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .overview-search {
    width: 100%;
  }

  .overview-search-row {
    justify-content: stretch;
  }
}
</style>
