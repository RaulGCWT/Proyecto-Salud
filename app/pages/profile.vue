<template>
  <div class="profile-page">
    <section class="profile-shell">
      <header class="page-header">
        <div class="page-heading">
          <p class="page-eyebrow">Authenticated session</p>
          <h1 class="page-title">My Profile</h1>
          <p class="page-subtitle">
            Profile information is read directly from the current authenticated session and its access context.
          </p>
        </div>
      </header>

      <section class="profile-card">
        <div class="profile-grid">
          <aside class="identity-panel">
            <div class="identity-head">
              <div class="avatar" aria-hidden="true">
                {{ userInitials }}
              </div>

              <div class="identity-copy">
                <h2>{{ userName }}</h2>
              </div>
            </div>

            <div class="identity-meta">
              <div class="meta-row">
                <span>Tenant</span>
                <strong>{{ tenantLabel }}</strong>
              </div>

              <div class="meta-row">
                <span>Role</span>
                <strong>{{ roleLabel }}</strong>
              </div>
            </div>
          </aside>

          <div class="details-panel">
            <div class="details-header">
              <p class="section-eyebrow">Account data</p>
              <h3>Session details</h3>
            </div>

            <div class="details-grid">
              <div class="detail-box">
                <span class="detail-label">Full name</span>
                <strong>{{ userName }}</strong>
              </div>

              <div class="detail-box">
                <span class="detail-label">Email</span>
                <strong>{{ userEmailLabel }}</strong>
              </div>

              <div class="detail-box">
                <span class="detail-label">Residence</span>
                <strong>{{ residenceLabel }}</strong>
              </div>

              <div class="detail-box">
                <span class="detail-label">Resident ID</span>
                <strong>{{ residentIdLabel }}</strong>
              </div>

              <div class="detail-box detail-box--wide">
                <span class="detail-label">Groups</span>
                <div class="groups-list">
                  <span v-for="group in userGroups" :key="group" class="group-tag">
                    {{ group }}
                  </span>
                  <span v-if="!userGroups.length" class="no-data">No groups assigned</span>
                </div>
              </div>
            </div>

            <div class="panel-actions">
              <button class="action-button action-button--danger" type="button" @click="handleLogout">
                <span class="material-symbols-outlined" aria-hidden="true">logout</span>
                <span>Log out</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { buildAccessContext } from '~/utils/accessContext'

useHead({
  title: 'Clinical Sentinel | Profile'
})

const auth = useAuthStore()

const user = computed(() => auth.user || {})
const accessContext = computed(() => buildAccessContext(user.value))

const userName = computed(() => user.value?.name || 'Unknown user')
const userEmailLabel = computed(() => user.value?.email || 'No email available')
const tenantLabel = computed(() => user.value?.tenantKey || 'Not assigned')
const roleLabel = computed(() => user.value?.role || accessContext.value.role || user.value?.groups?.[0] || 'Not assigned')
const residenceLabel = computed(() => accessContext.value.residenceId || 'Not assigned')
const residentIdLabel = computed(() => accessContext.value.residentId || 'Not assigned')
const userGroups = computed(() => Array.isArray(user.value?.groups) ? user.value.groups : [])

const userInitials = computed(() => {
  const name = String(userName.value || '').trim()
  if (!name) return '?'

  const parts = name.split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'

  return parts.slice(0, 2).map(part => part.charAt(0).toUpperCase()).join('')
})

const handleLogout = () => {
  auth.logout()
}
</script>

<style scoped>
.profile-page {
  display: grid;
}

.profile-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  padding-bottom: 12px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.page-eyebrow,
.section-eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 900;
  color: #2559bd;
}

.page-title {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.page-subtitle {
  margin: 8px 0 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
  max-width: 720px;
}

.profile-card {
  width: 100%;
  padding: 18px;
  border-radius: 28px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 18px 40px var(--surface-shadow);
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(240px, 280px) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
}

.identity-panel,
.details-panel {
  border-radius: 24px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel);
  padding: 18px;
}

.identity-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.identity-head {
  display: grid;
  justify-items: center;
  gap: 10px;
  text-align: center;
}

.avatar {
  width: 84px;
  height: 84px;
  border-radius: 20px;
  background: linear-gradient(135deg, #00327d, #0047ab);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.85rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  box-shadow: 0 20px 40px rgba(0, 50, 125, 0.18);
}

.identity-copy h2 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.25rem;
  font-weight: 900;
}

.identity-copy p {
  margin: 4px 0 0;
  color: var(--text-muted);
  word-break: break-word;
}

.identity-meta {
  display: grid;
  gap: 7px;
}

.meta-row,
.detail-box {
  padding: 10px 12px;
  border-radius: 13px;
  background: var(--surface-panel-strong);
  border: 1px solid var(--surface-border);
}

.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.meta-row span,
.detail-label {
  color: var(--text-muted);
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.meta-row strong,
.detail-box strong {
  color: var(--text-main);
  font-weight: 800;
  word-break: break-word;
  line-height: 1.4;
}

.details-panel {
  display: grid;
  gap: 12px;
}

.details-header h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.15rem;
  font-weight: 900;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.detail-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-box--wide {
  grid-column: 1 / -1;
}

.groups-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 2px;
}

.group-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.24);
  font-size: 0.78rem;
  font-weight: 800;
}

.no-data {
  color: var(--text-muted);
  font-size: 0.9rem;
  font-style: italic;
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 2px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid transparent;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease, background 0.2s ease;
}

.action-button:hover {
  transform: translateY(-1px);
}

.action-button--danger {
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.14);
  box-shadow: 0 10px 22px rgba(239, 68, 68, 0.05);
}

:global(.dark-mode) .profile-card {
  background: var(--surface-card);
  border-color: var(--surface-border);
  box-shadow: 0 18px 40px var(--surface-shadow);
}

:global(.dark-mode) .identity-panel,
:global(.dark-mode) .details-panel {
  background: var(--surface-panel);
  border-color: var(--surface-border);
}

:global(.dark-mode) .meta-row,
:global(.dark-mode) .detail-box {
  background: var(--surface-panel-strong);
  border-color: var(--surface-border);
}

:global(.dark-mode) .group-tag {
  background: rgba(37, 99, 235, 0.18);
  color: #bfdbfe;
  border-color: rgba(59, 130, 246, 0.24);
}

:global(.dark-mode) .action-button--danger {
  background: rgba(127, 29, 29, 0.18);
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.24);
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.18);
}

:global(.dark-mode) .identity-copy h2,
:global(.dark-mode) .details-header h3,
:global(.dark-mode) .meta-row strong,
:global(.dark-mode) .detail-box strong {
  color: var(--text-main);
}

:global(.dark-mode) .identity-copy p,
:global(.dark-mode) .meta-row span,
:global(.dark-mode) .detail-label,
:global(.dark-mode) .no-data {
  color: var(--text-muted);
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}

@media (max-width: 1100px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .profile-card {
    padding: 14px;
  }

  .identity-panel,
  .details-panel {
    padding: 16px;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .detail-box--wide {
    grid-column: auto;
  }

  .meta-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
