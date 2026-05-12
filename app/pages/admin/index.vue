<template>
  <div class="admin-dashboard">
    <UiPageHeader
      eyebrow="Administration Panel"
      title="Admin Dashboard"
      subtitle="System overview and quick access to management sections."
    />

    <div class="stats-bar">
      <div v-for="card in summaryCards" :key="card.label" class="stat-item">
        <strong class="stat-value">{{ card.value }}</strong>
        <span class="stat-label">{{ card.label }}</span>
        <span class="stat-note">{{ card.meta }}</span>
      </div>
    </div>

    <section class="quicklinks-section">
      <h2 class="section-title">Quick access</h2>
      <div class="quicklinks-grid">
        <NuxtLink
          v-for="link in quickLinks"
          :key="link.title"
          :to="link.to"
          class="quicklink-card"
          :style="`--accent: ${link.color}`"
        >
          <div class="quicklink-icon">
            <span class="material-symbols-outlined" aria-hidden="true">{{ link.icon }}</span>
          </div>
          <strong class="quicklink-title">{{ link.title }}</strong>
          <p class="quicklink-description">{{ link.description }}</p>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUsersManagement } from '~/composables/users/useUsersManagement'

useHead({ title: 'Clinical Sentinel | Admin Dashboard' })

const { summaryCards: rawCards } = useUsersManagement()

// Mismo orden que los quick links: Staff · Residents · Beds · Families · Invites
const STATS_ORDER = ['Staff', 'Residents', 'Beds', 'Families', 'Invites']
const summaryCards = computed(() => {
  const map = Object.fromEntries((rawCards.value || []).map(c => [c.label, c]))
  return STATS_ORDER.map(label => map[label]).filter(Boolean)
})

const quickLinks = [
  { icon: 'manage_accounts',  title: 'Staff',       description: 'Manage your staff team.',               to: '/admin/staff',       color: '#6d28d9' },
  { icon: 'person',           title: 'Residents',   description: 'Create and assign residents to beds.',  to: '/admin/residents',   color: '#047857' },
  { icon: 'sensors',          title: 'Devices',     description: 'Manage beds and monitor connections.',  to: '/admin/devices',     color: '#2559bd' },
  { icon: 'family_restroom',  title: 'Family',      description: 'Family users and their access.',        to: '/admin/family',      color: '#b45309' },
  { icon: 'mail',             title: 'Invitations', description: 'Pending and sent family invitations.',  to: '/admin/invitations', color: '#b91c1c' }
]
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

/* ── Stats bar ── */
.stats-bar {
  display: flex;
  gap: 0;
  padding: 20px 28px;
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 8px 24px var(--surface-shadow);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 0 24px;
  border-right: 1px solid var(--surface-border);
}

.stat-item:first-child { padding-left: 0; }
.stat-item:last-child  { padding-right: 0; border-right: none; }

.stat-value {
  font-size: clamp(1.8rem, 2.5vw, 2.4rem);
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
  line-height: 1;
}

.stat-label {
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.stat-note {
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* ── Quick links ── */
.section-title {
  margin: 0 0 14px;
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
}

.quicklinks-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.quicklink-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  padding: 28px 16px 22px;
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 8px 24px var(--surface-shadow);
  text-decoration: none;
  color: var(--text-main);
  border-top: 3px solid var(--accent);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.quicklink-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px color-mix(in srgb, var(--accent) 15%, transparent);
}

.quicklink-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
}

.quicklink-icon .material-symbols-outlined { font-size: 1.5rem; }

.quicklink-title {
  font-size: 0.98rem;
  font-weight: 900;
  color: var(--text-main);
}

.quicklink-description {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}

@media (max-width: 1100px) {
  .stats-bar { flex-wrap: wrap; }
  .stat-item { flex: 1 1 40%; border-right: none; padding: 10px 0; border-bottom: 1px solid var(--surface-border); }
  .quicklinks-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .quicklinks-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
