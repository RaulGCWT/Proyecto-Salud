<template>
  <div class="devices-page">
    <section class="summary-grid">
      <article class="summary-card summary-total">
        <div class="summary-card-top">
          <span class="summary-badge" aria-hidden="true">
            <svg viewBox="0 0 24 24" class="summary-icon" role="img">
              <rect x="4" y="5" width="16" height="12" rx="3" fill="none" stroke="currentColor" stroke-width="1.8" />
              <circle cx="8" cy="11" r="1.1" fill="currentColor" />
              <circle cx="12" cy="11" r="1.1" fill="currentColor" />
              <circle cx="16" cy="11" r="1.1" fill="currentColor" />
              <path d="M7 19h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </span>
          <span class="summary-chip">Fleet</span>
        </div>
        <span class="summary-title">Total Devices</span>
        <strong class="summary-value">{{ deviceStats.total }}</strong>
        <p class="summary-note">Accessible inventory within your permission scope.</p>
      </article>

      <article class="summary-card summary-online">
        <div class="summary-card-top">
          <span class="summary-badge" aria-hidden="true">
            <svg viewBox="0 0 24 24" class="summary-icon" role="img">
              <path d="M5 11a9 9 0 0 1 14 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              <path d="M8 14a5 5 0 0 1 8 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              <path d="M11 17a1 1 0 1 1 2 0" fill="currentColor" />
            </svg>
          </span>
          <span class="summary-chip">Connected</span>
        </div>
        <span class="summary-title">Online Devices</span>
        <strong class="summary-value">{{ deviceStats.online }}</strong>
        <p class="summary-note">Units receiving telemetry in real time.</p>
      </article>

      <article class="summary-card summary-offline">
        <div class="summary-card-top">
          <span class="summary-badge" aria-hidden="true">
            <svg viewBox="0 0 24 24" class="summary-icon" role="img">
              <path d="M5 11a9 9 0 0 1 8.5-4.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              <path d="M8.2 14.2a5 5 0 0 1 3.8-1.7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              <path d="M4.5 4.5 19.5 19.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </span>
          <span class="summary-chip">Disconnected</span>
        </div>
        <span class="summary-title">Offline Devices</span>
        <strong class="summary-value">{{ deviceStats.offline }}</strong>
        <p class="summary-note">Devices requiring attention or reconnection.</p>
      </article>
    </section>

    <section class="filters-panel">
      <div class="search-box">
        <span class="search-chip">Search</span>
        <input v-model="filters.search" type="text" placeholder="Search by name or MAC..." autocomplete="off" />
      </div>

      <div class="select-group">
        <div class="filter-dropdown" :class="{ 'filter-dropdown--open': activeFilterMenu === 'status' }">
          <button class="filter-trigger" type="button" @click="toggleFilterMenu('status')">
            <span>Status</span>
            <strong>{{ filterLabels.status[filters.status] }}</strong>
            <span class="filter-caret">▾</span>
          </button>
          <div v-if="activeFilterMenu === 'status'" class="filter-menu">
            <button
              v-for="option in filterOptions.status"
              :key="option.value"
              type="button"
              class="filter-option"
              :class="{ 'filter-option--active': filters.status === option.value }"
              @click="selectFilterOption('status', option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <div class="filter-dropdown" :class="{ 'filter-dropdown--open': activeFilterMenu === 'type' }">
          <button class="filter-trigger" type="button" @click="toggleFilterMenu('type')">
            <span>Type</span>
            <strong>{{ filterLabels.type[filters.type] }}</strong>
            <span class="filter-caret">▾</span>
          </button>
          <div v-if="activeFilterMenu === 'type'" class="filter-menu">
            <button
              v-for="option in filterOptions.type"
              :key="option.value"
              type="button"
              class="filter-option"
              :class="{ 'filter-option--active': filters.type === option.value }"
              @click="selectFilterOption('type', option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <div class="filter-dropdown" :class="{ 'filter-dropdown--open': activeFilterMenu === 'presence' }">
          <button class="filter-trigger" type="button" @click="toggleFilterMenu('presence')">
            <span>Presence</span>
            <strong>{{ filterLabels.presence[filters.presence] }}</strong>
            <span class="filter-caret">▾</span>
          </button>
          <div v-if="activeFilterMenu === 'presence'" class="filter-menu">
            <button
              v-for="option in filterOptions.presence"
              :key="option.value"
              type="button"
              class="filter-option"
              :class="{ 'filter-option--active': filters.presence === option.value }"
              @click="selectFilterOption('presence', option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <button class="btn-reset" type="button" @click="resetFilters">Reset</button>
      </div>
    </section>

    <section class="inventory-panel">
      <div class="panel-header">
        <div>
          <p class="panel-eyebrow">Inventory</p>
          <h3 class="panel-title">Device list</h3>
          <p class="panel-subtitle">{{ filteredBeds.length }} units matched</p>
        </div>

        <button class="panel-action" type="button" @click="refreshInventory">Refresh</button>
      </div>

      <div class="table-wrapper">
        <table class="devices-table">
          <thead>
            <tr>
              <th>MAC / UUID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Connection</th>
              <th>Presence</th>
              <th>Last event</th>
              <th v-if="canEditDevices">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bed in filteredBeds" :key="bed.mac">
              <td><code class="mac-code">{{ bed.mac }}</code></td>
              <td>
                <div class="device-name">
                  <strong>{{ bed.name }}</strong>
                  <span class="device-subtitle">Assigned owner: {{ bed.ownerId || 'Unassigned' }}</span>
                </div>
              </td>
              <td><span :class="['type-badge', getTypeTone(bed.type)]">{{ bed.type }}</span></td>
              <td><span :class="['connection-badge', bed.isOnline ? 'badge-online' : 'badge-offline']">{{ bed.isOnline ? 'Connected' : 'Disconnected' }}</span></td>
              <td><span :class="['presence-badge', getPresenceTone(bed.presence)]">{{ bed.presence }}</span></td>
              <td><span class="event-value">{{ bed.lastEventDate }}</span></td>
              <td v-if="canEditDevices">
                <button class="edit-button" type="button" title="Edit device" aria-label="Edit device" @click="editDevice(bed)">
                  <span class="edit-icon" aria-hidden="true">⚙</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="health-strip">
      <div class="panel-header health-header">
        <div>
          <p class="panel-eyebrow">Connection health</p>
          <h3 class="panel-title">Heartbeat snapshot</h3>
          <p class="panel-subtitle">Quick view of the most recent active devices in scope.</p>
        </div>
      </div>

      <div class="health-grid">
        <article v-for="card in healthCards" :key="card.mac" class="health-card" :class="{ 'health-card--online': card.isOnline }">
          <div class="health-card-top">
            <div>
              <p class="health-mac">{{ card.mac }}</p>
              <h4 class="health-name">{{ card.name }}</h4>
            </div>
            <span :class="['health-state', card.isOnline ? 'health-state--online' : 'health-state--offline']">{{ card.isOnline ? 'ON' : 'OFF' }}</span>
          </div>

          <div class="health-visual" aria-hidden="true">
            <div v-if="card.isOnline" class="sparkline">
              <span
                v-for="(bar, index) in card.sparkline"
                :key="`${card.mac}-${index}`"
                class="spark-bar"
                :style="{ height: `${bar}%` }"
              />
            </div>
            <div v-else class="health-visual-empty">
              <span class="health-visual-text">{{ card.lastSeenLabel }}</span>
            </div>
          </div>

          <div class="health-meta">
            <div>
              <span class="health-meta-label">Connection age</span>
              <strong>{{ card.connectionAge }}</strong>
            </div>
            <div>
              <span class="health-meta-label">Session count</span>
              <strong>{{ card.sessionCount }}</strong>
            </div>
            <div>
              <span class="health-meta-label">Signal freshness</span>
              <strong :class="['health-freshness', card.freshnessTone]">{{ card.signalFreshness }}</strong>
            </div>
          </div>
        </article>
      </div>
    </section>

    <DeviceEditModal :is-open="isEditing" :device="editingBed" :owner-options="ownerOptions" @close="closeModal" @save="saveChanges" />
  </div>
</template>

<script setup>
import { useDevicesPage } from '~/composables/devices/useDevicesPage'
import DeviceEditModal from '~/components/DeviceEditModal.vue'
import { onBeforeUnmount, onMounted, ref } from 'vue'

useHead({
  title: 'Clinical Sentinel | Devices'
})

const {
  accessibleBeds,
  deviceStats,
  filteredBeds,
  healthCards,
  ownerOptions,
  filters,
  lastInventorySync,
  canEditDevices,
  isEditing,
  editingBed,
  refreshInventory,
  checkConnections,
  editDevice,
  closeModal,
  saveChanges,
  resetFilters,
  getTypeTone,
  getPresenceTone
} = useDevicesPage()

const activeFilterMenu = ref('')

const filterOptions = {
  status: [
    { label: 'All Statuses', value: 'all' },
    { label: 'Connected', value: 'online' },
    { label: 'Disconnected', value: 'offline' }
  ],
  type: [
    { label: 'All Types', value: 'all' },
    { label: 'Critical Care', value: 'Critical Care' },
    { label: 'Standard', value: 'Standard' }
  ],
  presence: [
    { label: 'All Presence', value: 'all' },
    { label: 'Occupied', value: 'Occupied' },
    { label: 'Empty', value: 'Empty' }
  ]
}

const filterLabels = {
  status: {
    all: 'All Statuses',
    online: 'Connected',
    offline: 'Disconnected'
  },
  type: {
    all: 'All Types',
    'Critical Care': 'Critical Care',
    Standard: 'Standard'
  },
  presence: {
    all: 'All Presence',
    Occupied: 'Occupied',
    Empty: 'Empty'
  }
}

const toggleFilterMenu = (menuName) => {
  activeFilterMenu.value = activeFilterMenu.value === menuName ? '' : menuName
}

const selectFilterOption = (field, value) => {
  filters.value[field] = value
  activeFilterMenu.value = ''
}

const closeFilterMenu = (event) => {
  const target = event.target
  if (target?.closest?.('.filter-dropdown')) return
  activeFilterMenu.value = ''
}

onMounted(() => {
  document.addEventListener('click', closeFilterMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeFilterMenu)
})
</script>

<style scoped>
.devices-page { display: flex; flex-direction: column; gap: 24px; max-width: 1440px; margin: 0 auto; padding-bottom: 12px; font-family: 'Inter', sans-serif; color: var(--text-main); }
.devices-page *, .devices-page *::before, .devices-page *::after { font-family: inherit; }
.devices-page h1, .devices-page h2, .devices-page h3, .devices-page h4, .devices-page h5, .devices-page h6 { margin: 0; font-weight: 900; letter-spacing: -0.04em; line-height: 1.05; }
.devices-page p, .devices-page span, .devices-page button, .devices-page input, .devices-page select, .devices-page td, .devices-page th, .devices-page label { font-family: inherit; }
.summary-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.summary-card { position: relative; overflow: hidden; padding: 22px; border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.16); background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95)); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04); }
.summary-card::after { content: ''; position: absolute; inset: auto -18% -38% auto; width: 180px; height: 180px; border-radius: 50%; background: radial-gradient(circle, rgba(37, 89, 189, 0.08), transparent 70%); pointer-events: none; }
.summary-card-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.summary-badge { width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center; font-size: 0.82rem; font-weight: 900; letter-spacing: 0.08em; color: #ffffff; }
.summary-icon { width: 24px; height: 24px; display: block; }
.summary-chip { padding: 7px 10px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.14em; }
.summary-total .summary-badge { background: linear-gradient(135deg, #0f172a, #2559bd); }
.summary-online .summary-badge { background: linear-gradient(135deg, #10b981, #14b8a6); }
.summary-offline .summary-badge { background: linear-gradient(135deg, #ef4444, #f97316); }
.summary-total .summary-chip { color: #2559bd; background: rgba(37, 89, 189, 0.08); }
.summary-online .summary-chip { color: #047857; background: rgba(16, 185, 129, 0.08); }
.summary-offline .summary-chip { color: #b91c1c; background: rgba(239, 68, 68, 0.08); }
.summary-title { display: block; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.18em; text-transform: uppercase; color: #5b6b84; }
.summary-value { display: block; margin: 10px 0 14px; font-size: clamp(1.9rem, 2.6vw, 2.4rem); font-weight: 900; line-height: 1; letter-spacing: -0.04em; color: var(--text-main); }
.summary-note { margin: 0; color: var(--text-muted); font-size: 0.92rem; line-height: 1.5; }
.filters-panel { display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap; padding: 14px 16px; border-radius: 20px; border: 1px solid var(--border-color); background: rgba(255, 255, 255, 0.82); box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04); }
.search-box { position: relative; flex: 1 1 320px; min-width: 260px; }
.search-chip { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); padding: 5px 9px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; color: #2559bd; background: rgba(37, 89, 189, 0.08); }
.search-box input { width: 100%; padding: 11px 14px 11px 90px; border-radius: 14px; border: 1px solid rgba(148, 163, 184, 0.2); background: var(--bg-main); color: var(--text-main); outline: none; box-sizing: border-box; }
.search-box input::placeholder { color: var(--text-muted); }
.select-group { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; flex: 1 1 440px; justify-content: flex-end; }
.filter-dropdown { position: relative; min-width: 190px; }
.filter-trigger { width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 11px 14px; border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.22); background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94)); color: var(--text-main); font-weight: 700; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03); cursor: pointer; transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; }
.filter-trigger:hover { border-color: rgba(37, 89, 189, 0.28); box-shadow: 0 12px 24px rgba(37, 89, 189, 0.08); transform: translateY(-1px); }
.filter-trigger span { font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase; color: #64748b; }
.filter-trigger strong { flex: 1; text-align: left; font-size: 0.92rem; font-weight: 800; color: var(--text-main); }
.filter-caret { color: #2559bd; font-size: 0.72rem; }
.filter-menu { position: absolute; top: calc(100% + 10px); left: 0; width: 100%; padding: 8px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.18); background: rgba(255, 255, 255, 0.98); box-shadow: 0 20px 40px rgba(15, 23, 42, 0.12); z-index: 20; }
.filter-option { width: 100%; display: flex; align-items: center; padding: 10px 12px; border: 0; border-radius: 12px; background: transparent; color: var(--text-main); font-weight: 700; text-align: left; cursor: pointer; transition: background 0.2s ease, color 0.2s ease; }
.filter-option:hover { background: rgba(37, 89, 189, 0.08); color: #2559bd; }
.filter-option--active { background: rgba(37, 89, 189, 0.12); color: #2559bd; }
.btn-reset { padding: 11px 14px; border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.2); background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92)); color: var(--text-main); font-weight: 800; cursor: pointer; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03); transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; }
.btn-reset:hover { border-color: rgba(37, 89, 189, 0.24); box-shadow: 0 12px 24px rgba(37, 89, 189, 0.08); transform: translateY(-1px); }
.btn-reset:focus { outline: none; box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.12); }
.inventory-panel { border-radius: 24px; border: 1px solid var(--border-color); background: var(--bg-card); box-shadow: 0 18px 40px rgba(15, 23, 42, 0.04); overflow: hidden; }
.panel-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 22px 22px 0; }
.panel-eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.68rem; font-weight: 900; color: #2559bd; }
.panel-title { margin: 0; font-size: 1.18rem; font-weight: 900; color: var(--text-main); }
.panel-subtitle { margin: 6px 0 0; color: var(--text-muted); font-size: 0.92rem; }
.panel-action { padding: 10px 14px; border-radius: 14px; border: 1px solid var(--surface-border); background: var(--surface-panel-strong); color: var(--text-main); font-weight: 800; cursor: pointer; box-shadow: 0 8px 20px var(--surface-shadow); }
.panel-action:hover { border-color: rgba(37, 89, 189, 0.24); box-shadow: 0 12px 24px rgba(37, 89, 189, 0.08); transform: translateY(-1px); }
.panel-action:focus { outline: none; box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.12); }

:global(.dark-mode) .devices-page .panel-action {
  background: var(--surface-panel-strong) !important;
  border-color: rgba(51, 65, 85, 0.78) !important;
  color: #f8fafc !important;
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.28) !important;
}

:global(.dark-mode) .devices-page .panel-action:hover {
  border-color: rgba(96, 165, 250, 0.34) !important;
  box-shadow: 0 14px 26px rgba(2, 6, 23, 0.36) !important;
}
.table-wrapper { overflow-x: auto; padding: 18px 22px 22px; }
.devices-table { width: 100%; min-width: 980px; border-collapse: separate; border-spacing: 0; }
.devices-table th { padding: 14px 16px; text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; color: #64748b; background: rgba(248, 250, 252, 0.8); border-bottom: 1px solid rgba(148, 163, 184, 0.18); }
.devices-table th:last-child { width: 88px; text-align: center; }
.devices-table th:first-child { border-top-left-radius: 16px; }
.devices-table th:last-child { border-top-right-radius: 16px; }
.devices-table td { padding: 16px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); color: var(--text-main); vertical-align: middle; }
.devices-table td:last-child { width: 88px; text-align: center; }
.devices-table tbody tr { transition: background 0.2s ease; }
.devices-table tbody tr:hover { background: rgba(248, 250, 252, 0.75); }
.mac-code { font-size: 0.8rem; font-weight: 800; letter-spacing: 0.06em; color: #64748b; }
.device-name { display: flex; flex-direction: column; gap: 4px; }
.device-name strong { font-size: 0.98rem; font-weight: 800; color: var(--text-main); }
.device-subtitle { font-size: 0.8rem; color: var(--text-muted); }
.type-badge, .connection-badge, .presence-badge { display: inline-flex; align-items: center; justify-content: center; padding: 6px 12px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; }
.type-standard { color: #2559bd; background: rgba(37, 89, 189, 0.08); }
.type-critical { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.type-pump { color: #7c3aed; background: rgba(139, 92, 246, 0.12); }
.type-life { color: #047857; background: rgba(16, 185, 129, 0.12); }
.badge-online { color: #047857; background: rgba(16, 185, 129, 0.12); }
.badge-offline { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.presence-occupied { color: #2559bd; background: rgba(37, 89, 189, 0.1); }
.presence-empty { color: #64748b; background: rgba(100, 116, 139, 0.1); }
.event-value { font-size: 0.84rem; color: var(--text-muted); }
.edit-button { width: 36px; height: 36px; display: inline-flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.18); background: rgba(255, 255, 255, 0.88); color: #4b5563; cursor: pointer; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03); transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease, color 0.2s ease; }
.edit-button:hover { border-color: rgba(37, 89, 189, 0.24); box-shadow: 0 12px 24px rgba(37, 89, 189, 0.08); color: #2559bd; transform: translateY(-1px); }
.edit-button:focus { outline: none; box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.12); }
.edit-icon { font-size: 1rem; line-height: 1; }
.health-strip { display: flex; flex-direction: column; gap: 18px; }
.health-header { padding: 0; }
.health-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.health-card { display: flex; flex-direction: column; gap: 16px; min-height: 220px; padding: 18px; border-radius: 22px; border: 1px solid rgba(148, 163, 184, 0.16); background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(248, 250, 252, 0.92)); box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04); }
.health-card--online { border-color: rgba(16, 185, 129, 0.22); }
.health-card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.health-mac { margin: 0 0 4px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; color: #64748b; }
.health-name { margin: 0; font-size: 0.98rem; font-weight: 900; color: var(--text-main); }
.health-state { padding: 7px 10px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; }
.health-state--online { color: #047857; background: rgba(16, 185, 129, 0.12); }
.health-state--offline { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.health-visual { display: flex; align-items: center; justify-content: center; min-height: 72px; }
.sparkline { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); align-items: end; gap: 5px; width: 100%; min-height: 58px; padding: 8px 0 0; }
.spark-bar { display: block; width: 100%; border-radius: 999px; background: linear-gradient(180deg, #ff9b9b, #ef4444); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.16); opacity: 0.88; }
.health-visual-empty { display: flex; align-items: center; justify-content: center; width: 100%; min-height: 58px; }
.health-visual-text { font-size: 0.7rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; color: #94a3b8; text-align: center; }
.health-meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: auto; }
.health-meta div { display: flex; flex-direction: column; gap: 4px; padding-top: 8px; border-top: 1px solid rgba(148, 163, 184, 0.14); }
.health-meta-label { font-size: 0.66rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.health-meta strong { font-size: 0.82rem; font-weight: 800; color: var(--text-main); }
.health-freshness { display: inline-flex; }
.health-freshness { padding: 5px 10px; border-radius: 999px; width: fit-content; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.08em; text-transform: uppercase; }
.search-chip, .filter-trigger span, .filter-option, .btn-reset, .edit-button { font-family: inherit; }
.search-chip { font-size: 0.66rem; letter-spacing: 0.16em; font-weight: 900; }
.filter-trigger span { font-size: 0.66rem; letter-spacing: 0.16em; font-weight: 900; }
.filter-trigger strong { font-size: 0.9rem; font-weight: 900; letter-spacing: -0.01em; }
.filter-option { font-size: 0.92rem; font-weight: 800; }
.btn-reset { font-size: 0.82rem; letter-spacing: 0.08em; text-transform: uppercase; }
.edit-button { font-size: 0.95rem; font-weight: 900; }
.freshness-fresh { color: #047857; }
.freshness-warm { color: #2559bd; }
.freshness-stale { color: #b45309; }
.freshness-silent { color: #b91c1c; }
@media (max-width: 900px) { .summary-grid { grid-template-columns: 1fr; } .panel-header { flex-direction: column; align-items: flex-start; } }
@media (max-width: 900px) { .health-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 768px) { .filters-panel { align-items: stretch; } .search-box, .select-group { flex: 1 1 100%; max-width: none; } .select-group { justify-content: stretch; } .filter-dropdown, .btn-reset { flex: 1 1 160px; min-width: 0; } .health-grid { grid-template-columns: 1fr; } .health-meta { grid-template-columns: 1fr; } .health-card { min-height: unset; } }
</style>
