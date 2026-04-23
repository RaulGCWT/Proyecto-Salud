<template>
  <div class="dashboard-wrapper" :class="{ 'dark-mode': isDark }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-block">
          <img src="../images/logo.png" alt="Welltech Logo">
          <span class="brand-subtitle">IoT Health</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <NuxtLink
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          active-class="active"
        >
          <span class="material-symbols-outlined nav-icon" aria-hidden="true">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-row">
          <p class="user-display"><strong>{{ displayUserName }}</strong></p>
          <button @click="toggleDark" class="mini-mode-toggle" :title="isDark ? 'Light mode' : 'Dark mode'">
            <span class="material-symbols-outlined" aria-hidden="true">
              {{ isDark ? 'light_mode' : 'dark_mode' }}
            </span>
          </button>
        </div>
        <button @click="handleLogout" class="btn-logout">Log out</button>
      </div>
    </aside>

    <main class="content-area">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { APP_NAV_ITEMS } from '~/utils/navigation'

const auth = useAuthStore()
const isDark = ref(false)

const menuItems = computed(() => {
  return APP_NAV_ITEMS.filter((item) => {
    if (!item.permission) {
      return true
    }

    return auth.permissions.includes(item.permission)
  })
})

const displayUserName = computed(() => auth.user?.name || 'Usuario')

const handleLogout = () => {
  auth.logout()
}

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

:root {
  --bg-main: #f7f9fb;
  --bg-card: #ffffff;
  --surface-card: #ffffff;
  --surface-card-soft: rgba(248, 250, 252, 0.95);
  --surface-card-strong: rgba(255, 255, 255, 0.98);
  --surface-card-tinted: rgba(37, 89, 189, 0.08);
  --surface-hero: linear-gradient(135deg, rgba(37, 89, 189, 0.08), rgba(255, 255, 255, 0.96));
  --surface-panel: rgba(255, 255, 255, 0.75);
  --surface-panel-strong: #f8fafc;
  --surface-plot: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.95));
  --surface-border: rgba(148, 163, 184, 0.16);
  --surface-shadow: rgba(15, 23, 42, 0.06);
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
}

.dark-mode {
  --bg-main: #0b1220;
  --bg-card: #020617;
  --surface-card: #020617;
  --surface-card-soft: rgba(15, 23, 42, 0.96);
  --surface-card-strong: rgba(2, 6, 23, 0.98);
  --surface-card-tinted: rgba(37, 89, 189, 0.16);
  --surface-hero: linear-gradient(135deg, rgba(2, 6, 23, 0.99), rgba(15, 23, 42, 0.97));
  --surface-panel: rgba(2, 6, 23, 0.98);
  --surface-panel-strong: rgba(2, 6, 23, 0.96);
  --surface-plot: linear-gradient(180deg, rgba(2, 6, 23, 0.92), rgba(15, 23, 42, 0.96));
  --surface-border: rgba(51, 65, 85, 0.78);
  --surface-shadow: rgba(2, 6, 23, 0.34);
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --border-color: #1f2937;
  color-scheme: dark;
}

body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-main) !important;
  color: var(--text-main);
  transition: background-color 0.3s ease;
}

.dashboard-wrapper {
  display: flex;
  min-height: 100vh;
  background: var(--bg-main);
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: white;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-header {
  padding: 22px;
  background: rgba(2, 6, 23, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.logo-block img {
  max-width: 180px;
  height: auto;
  max-height: 60px;
  object-fit: contain;
  filter: brightness(1.1);
}

.brand-subtitle {
  font-size: 0.75rem;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #94a3b8;
  text-decoration: none;
  transition: 0.2s ease;
  border-right: 4px solid transparent;
}

.nav-icon {
  width: 24px;
  display: inline-flex;
  justify-content: center;
  font-size: 1.1rem;
}

.nav-item:hover,
.nav-item.active {
  color: white;
  background: rgba(59, 130, 246, 0.1);
  border-right-color: #3b82f6;
}

.content-area {
  margin-left: 260px;
  padding: 40px;
  width: calc(100% - 260px);
  min-height: 100vh;
  background: var(--bg-main);
}

.dark-mode .dashboard-wrapper {
  background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
}

.dark-mode .content-area {
  background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
}

.dark-mode .content-area :is(
  .card,
  .chart-shell,
  .table-container,
  .metric-card,
  .metric-card.is-empty,
  .summary-card,
  .toolbar-panel,
  .section-card,
  .entry-row,
  .entry-card,
  .table-card,
  .table-head,
  .table-row,
  .filters-panel,
  .health-card,
  .rule-card,
  .modal-card,
  .panel,
  .toast,
  .content-shell,
  .hero-card,
  .stats-card,
  .details-panel,
  .bg-white,
  .bg-surface,
  .bg-surface-container,
  .bg-surface-container-low,
  .bg-surface-container-high,
  .bg-surface-container-highest,
  .bg-surface-container-lowest
) {
  background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.95)) !important;
  border-color: rgba(51, 65, 85, 0.76) !important;
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.34) !important;
  color: var(--text-main) !important;
  background-image: none !important;
}

.dark-mode .content-area :is(
  .summary-card,
  .section-card,
  .entry-card,
  .entry-row,
  .table-card,
  .table-row,
  .health-card,
  .rule-card,
  .modal-card,
  .panel
) {
  color: var(--text-main);
}

.dark-mode .content-area :is(
  .search,
  .search-input,
  .search-box input,
  .form-group input,
  .form-group select,
  .filter-trigger,
  .severity-button,
  .icon-button,
  .action-button--ghost,
  .section-action,
  .btn-muted,
  .btn-reset,
  .page-button,
  .page-number,
  input,
  select,
  textarea
) {
  background: rgba(2, 6, 23, 0.9) !important;
  border-color: rgba(51, 65, 85, 0.72) !important;
  color: var(--text-main) !important;
}

.dark-mode .content-area :is(.search::placeholder, .search-input::placeholder, .search-box input::placeholder, input::placeholder, textarea::placeholder) {
  color: var(--text-muted);
}

.dark-mode .toolbar-panel,
.dark-mode .filters-panel {
  backdrop-filter: blur(14px);
}

.dark-mode .mini-mode-toggle,
.dark-mode .sidebar-footer .btn-logout {
  border-color: rgba(148, 163, 184, 0.16);
}

.sidebar-footer {
  padding: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.user-display {
  font-size: 0.85rem;
  color: #3b82f6;
  margin: 0;
}

.mini-mode-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s ease;
}

.mini-mode-toggle:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}

.btn-logout {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  box-shadow: 0 12px 24px rgba(239, 68, 68, 0.18);
}

.dark-mode .card,
.dark-mode .chart-shell,
.dark-mode .table-container {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-main) !important;
}

.dark-mode .content-area :is(
  .btn,
  button,
  a.btn,
  .action-btn,
  .action-button,
  .primary-button,
  .secondary-button
) {
  border-color: rgba(51, 65, 85, 0.72);
}

@media (max-width: 900px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
  }

  .content-area {
    margin-left: 0;
    width: 100%;
    padding: 24px 18px 28px;
  }
}
</style>
