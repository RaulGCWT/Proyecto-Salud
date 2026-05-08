<template>
  <div class="alerts-page">
    <section class="page-shell">
      <UiPageHeader eyebrow="Alert History" title="Clinical Alert History" subtitle="Audit log of clinical events and system-generated diagnostic notifications.">
        <template #actions>
          <div class="refresh-meta">
            <span class="refresh-meta__label">Last refreshed</span>
            <span class="refresh-meta__value">{{ lastRefreshedLabel }}</span>
          </div>
          <button class="action-button action-button--ghost" type="button" :disabled="isRefreshing" @click="refreshAlerts">
            <span class="material-symbols-outlined" aria-hidden="true">refresh</span>
            <span>{{ isRefreshing ? 'Refreshing...' : 'Refresh' }}</span>
          </button>
          <template v-if="canClearHistory">
            <template v-if="!pendingClearHistory">
              <button class="action-button action-button--danger" type="button" @click="pendingClearHistory = true">
                <span class="material-symbols-outlined" aria-hidden="true">delete_sweep</span>
                <span>Clear History</span>
              </button>
            </template>
            <template v-else>
              <span class="confirm-label">Clear all alerts?</span>
              <button class="action-button action-button--ghost" type="button" @click="pendingClearHistory = false">Cancel</button>
              <button class="action-button action-button--danger" type="button" @click="confirmClearHistory">Clear All</button>
            </template>
          </template>
        </template>
      </UiPageHeader>

      <section class="summary-grid">
        <UiSummaryCard icon="notification_important" label="Total Alerts" :value="totalAlerts.toLocaleString()" :note="`${pendingAlerts} require review right now.`" tone="blue" />
        <UiSummaryCard icon="pending_actions" label="Pending Review" :value="pendingAlerts.toLocaleString()" note="Requires immediate attention." tone="red" />
        <UiSummaryCard icon="task_alt" label="Resolution Rate" :value="`${resolutionRate}%`" note="Percentage of alerts marked as read." tone="teal" />
      </section>

      <section class="filters-card">
        <UiSearchInput v-model="searchQuery" placeholder="Filter by MAC, Message or Sensor..." />

        <UiFilterDropdown label="Status" :model-value="activeStatusFilter" :options="statusFilters" @update:model-value="setStatusFilter" />
        <UiFilterDropdown label="Severity" :model-value="activeSeverityFilter" :options="severityFilters" @update:model-value="setSeverityFilter" />
        <UiFilterDropdown label="Device" :model-value="activeMacFilter" :options="deviceFilters" @update:model-value="setDeviceFilter" />
        <UiFilterDropdown label="Side" :model-value="activeSideFilter" :options="sideFilters" @update:model-value="setSideFilter" />

        <div class="result-chip">
          Filtered: {{ filteredAlerts.length }} results
        </div>
      </section>

      <section class="table-card">
        <div class="table-wrap">
          <table class="alerts-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Device</th>
                <th>Sensor</th>
                <th>Side</th>
                <th>Message</th>
                <th>State</th>
                <th>Severity</th>
                <th class="align-right">Actions</th>
              </tr>
            </thead>

            <tbody v-if="visibleAlerts.length">
              <tr v-for="alert in visibleAlerts" :key="alert.id" class="table-row">
                <td>
                  <div class="primary-cell">{{ alert.time }}</div>
                  <div class="secondary-cell">{{ alert.dateLabel }}</div>
                </td>
                <td>
                  <div class="device-cell">
                    <strong class="device-name">{{ getAlertDeviceName(alert) }}</strong>
                    <code class="mac-chip">{{ alert.mac }}</code>
                  </div>
                </td>
                <td>
                  <span :class="['sensor-chip', getSensorTone(alert.sensor)]">{{ alert.sensor }}</span>
                </td>
                <td>
                  <span
                    :class="['side-chip', alert.side && normalizeSideFilterValue(alert.side) !== 'all' ? 'side-chip--active' : 'side-chip--neutral']"
                  >
                    {{ formatSideLabel(alert.side) }}
                  </span>
                </td>
                <td>
                  <p class="message-cell" :title="alert.message">{{ alert.message }}</p>
                </td>
                <td>
                  <span :class="['status-chip', alert.status === 'READ' ? 'status-chip--read' : 'status-chip--pending']">
                    <span class="status-dot" aria-hidden="true"></span>
                    {{ alert.status === 'READ' ? 'READ' : 'PENDING' }}
                  </span>
                </td>
                <td>
                  <span :class="['severity-chip', getSeverityTone(alert.level)]">{{ alert.level }}</span>
                </td>
                <td class="align-right">
                  <div class="row-actions" @click.stop>
                    <button class="icon-button" type="button" :title="alert.status === 'READ' ? 'Mark as pending' : 'Mark as read'" @click="toggleAlertStatus(alert)">
                      <span class="material-symbols-outlined" aria-hidden="true">
                        {{ alert.status === 'READ' ? 'history' : 'check_circle' }}
                      </span>
                    </button>
                    <button class="icon-button" type="button" title="More actions" @click.stop="toggleAlertMenu(alert.id)">
                      <span class="material-symbols-outlined" aria-hidden="true">more_vert</span>
                    </button>

                    <div v-if="activeMenuId === alert.id" class="context-menu">
                      <button class="context-menu-item" type="button" @click="copyToClipboard(alert.mac)">
                        <span class="material-symbols-outlined" aria-hidden="true">content_copy</span>
                        <span>Copy MAC</span>
                      </button>
                      <template v-if="pendingDeleteAlertId !== alert.id">
                        <button class="context-menu-item context-menu-item--danger" type="button" @click.stop="pendingDeleteAlertId = alert.id">
                          <span class="material-symbols-outlined" aria-hidden="true">delete</span>
                          <span>Delete this alert</span>
                        </button>
                      </template>
                      <template v-else>
                        <div class="context-menu-confirm">
                          <span class="context-confirm-label">Delete this alert?</span>
                          <div class="context-confirm-actions">
                            <button class="context-menu-item" type="button" @click.stop="pendingDeleteAlertId = null">Cancel</button>
                            <button class="context-menu-item context-menu-item--danger" type="button" @click.stop="confirmDeleteAlert(alert.id)">Delete</button>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <UiEmptyState
          v-if="!visibleAlerts.length"
          icon="notifications_off"
          title="No alerts found"
          :message="searchQuery || activeStatusFilter !== 'all' || activeSeverityFilter !== 'all' || activeMacFilter !== 'all' || activeSideFilter !== 'all' ? 'Try adjusting your filters or search terms to find the clinical logs you\'re looking for.' : 'No alerts recorded in the database.'"
        >
          <template #action>
            <button class="empty-action" type="button" @click="resetFilters">Clear all filters</button>
          </template>
        </UiEmptyState>

        <footer class="table-footer">
          <p class="footer-text">
            Showing {{ pageStart }} to {{ pageEnd }} of {{ filteredAlerts.length }} alerts
          </p>

          <div class="pagination">
            <button class="page-button" type="button" :disabled="currentPage === 1" @click="previousPage">Prev</button>
            <button
              v-for="page in pageNumbers"
              :key="page"
              class="page-number"
              :class="{ 'page-number--active': page === currentPage }"
              type="button"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <button class="page-button" type="button" :disabled="currentPage === pageCount" @click="nextPage">Next</button>
          </div>
        </footer>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useHealthStore } from '~/stores/health'
import { useAuthStore } from '~/stores/auth'
import { PERMISSIONS } from '~/utils/permissions'

useHead({
  title: 'Clinical Alert History | Sentinel HQ'
})

const healthStore = useHealthStore()
const auth = useAuthStore()

const searchQuery = ref('')
const activeStatusFilter = ref('all')
const activeSeverityFilter = ref('all')
const activeMacFilter = ref('all')
const activeSideFilter = ref('all')
const currentPage = ref(1)
const activeMenuId = ref('')
const activeFilterMenu = ref('')
const isRefreshing = ref(false)
const lastRefreshedAt = ref(null)
const pendingClearHistory = ref(false)
const pendingDeleteAlertId = ref(null)
const pageSize = 10

const statusFilters = [
  { label: 'All', value: 'all' },
  { label: 'Read', value: 'read' },
  { label: 'Pending', value: 'pending' }
]

const severityFilters = [
  { label: 'All', value: 'all' },
  { label: 'Critical', value: 'critical' },
  { label: 'Warning', value: 'warning' },
  { label: 'Info', value: 'info' }
]

const sideFilters = [
  { label: 'All', value: 'all' },
  { label: 'Left', value: 'left' },
  { label: 'Right', value: 'right' }
]

const canClearHistory = computed(() => auth.permissions.includes(PERMISSIONS.ALERTS_CLEAR))
const totalAlerts = computed(() => healthStore.alertHistory.length)
const pendingAlerts = computed(() => healthStore.alertHistory.filter(alert => alert.status !== 'READ').length)
const resolutionRate = computed(() => {
  if (!totalAlerts.value) return 0
  return Math.round(((totalAlerts.value - pendingAlerts.value) / totalAlerts.value) * 1000) / 10
})
const statusLabel = computed(() => statusFilters.find(option => option.value === activeStatusFilter.value)?.label || 'All')
const severityLabel = computed(() => severityFilters.find(option => option.value === activeSeverityFilter.value)?.label || 'All')
const deviceFilters = computed(() => {
  const macs = new Set()

  healthStore.alertHistory.forEach((alert) => {
    const mac = String(alert.mac || '').trim()
    if (!mac) return
    macs.add(mac)
  })

  const options = Array.from(macs)
    .sort((left, right) => left.localeCompare(right))
    .map(value => ({ label: value, value }))

  return [{ label: 'All', value: 'all' }, ...options]
})
const deviceLabel = computed(() => deviceFilters.value.find(option => option.value === activeMacFilter.value)?.label || 'All')
const selectedSideLabel = computed(() => sideFilters.find(option => option.value === activeSideFilter.value)?.label || 'All')
const deviceLookup = computed(() => {
  const lookup = new Map()

  healthStore.deviceInventory.forEach((device) => {
    const deviceName = String(device.name || '').trim()
    const deviceMac = String(device.mac || '').trim().toLowerCase()
    const deviceId = String(device.deviceId || device.id || '').trim().toLowerCase()
    const label = deviceName || device.deviceId || device.mac || 'Unknown device'

    if (deviceMac) lookup.set(deviceMac, label)
    if (deviceId) lookup.set(deviceId, label)
  })

  return lookup
})
const lastRefreshedLabel = computed(() => {
  if (!lastRefreshedAt.value) return 'Never'

  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(lastRefreshedAt.value)
})

const normalizeSeverity = (value) => String(value || '').trim().toLowerCase()
const normalizeSideFilterValue = (value) => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'left' || normalized === 'right') return normalized
  return 'all'
}

const getSensorTone = (sensor) => {
  const value = String(sensor || '').toLowerCase()
  if (value.includes('hr')) return 'sensor-chip--blue'
  if (value.includes('resp') || value.includes('spo2')) return 'sensor-chip--teal'
  if (value.includes('temp')) return 'sensor-chip--amber'
  return 'sensor-chip--neutral'
}

const getSeverityTone = (severity) => {
  const normalized = normalizeSeverity(severity)
  if (normalized === 'critical') return 'severity-chip--critical'
  if (normalized === 'warning') return 'severity-chip--warning'
  return 'severity-chip--info'
}

const formatSideLabel = (value) => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'left') return 'Left'
  if (normalized === 'right') return 'Right'
  return 'All sides'
}

const normalizeSearchValue = (value) => String(value || '')
  .toLowerCase()
  .replace(/[^a-z0-9]/g, '')

const getAlertDeviceName = (alert = {}) => {
  const mac = String(alert.mac || '').trim().toLowerCase()
  const deviceId = String(alert.deviceId || '').trim().toLowerCase()
  return deviceLookup.value.get(mac) || deviceLookup.value.get(deviceId) || alert.deviceId || alert.mac || 'Unknown device'
}

const filteredAlerts = computed(() => {
  const query = normalizeSearchValue(searchQuery.value)

  return healthStore.alertHistory.filter((alert) => {
    const searchableValues = [alert.mac, alert.deviceId, getAlertDeviceName(alert), alert.sensor, alert.message, alert.dateLabel, alert.time, alert.side]
      .filter(Boolean)
      .map(value => normalizeSearchValue(value))

    const matchesQuery = !query || searchableValues.some(value => value.includes(query))

    const alertLevel = normalizeSeverity(alert.level)
    const alertStatus = normalizeSeverity(alert.status)
    const matchesStatus =
      activeStatusFilter.value === 'all'
      || (activeStatusFilter.value === 'read' && alertStatus === 'read')
      || (activeStatusFilter.value === 'pending' && alertStatus !== 'read')

    const matchesSeverity = activeSeverityFilter.value === 'all' || alertLevel === activeSeverityFilter.value
    const alertMac = String(alert.mac || '').trim()
    const matchesMac = activeMacFilter.value === 'all' || normalizeSearchValue(alertMac) === normalizeSearchValue(activeMacFilter.value)
    const alertSide = normalizeSideFilterValue(alert.side)
    const matchesSide =
      activeSideFilter.value === 'all'
      || (activeSideFilter.value === 'left' && alertSide === 'left')
      || (activeSideFilter.value === 'right' && alertSide === 'right')

    return matchesQuery && matchesStatus && matchesSeverity && matchesMac && matchesSide
  })
})

const sortAlertTimestamp = (alert = {}) => {
  const numericTimestamp = Number(alert.timestamp || 0)
  if (Number.isFinite(numericTimestamp) && numericTimestamp > 0) return numericTimestamp

  const parsed = Date.parse(`${alert.dateLabel || ''} ${alert.time || ''}`)
  return Number.isFinite(parsed) ? parsed : 0
}

const sortedAlerts = computed(() => [...filteredAlerts.value].sort((left, right) => {
  const leftPending = normalizeSeverity(left.status) !== 'read'
  const rightPending = normalizeSeverity(right.status) !== 'read'

  if (leftPending !== rightPending) return leftPending ? -1 : 1

  return sortAlertTimestamp(right) - sortAlertTimestamp(left)
}))

const pageCount = computed(() => Math.max(Math.ceil(filteredAlerts.value.length / pageSize), 1))

const visibleAlerts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedAlerts.value.slice(start, start + pageSize)
})

const pageStart = computed(() => (sortedAlerts.value.length ? (currentPage.value - 1) * pageSize + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * pageSize, sortedAlerts.value.length))

const pageNumbers = computed(() => {
  const totalPages = pageCount.value
  const current = currentPage.value
  const pages = []

  const start = Math.max(1, current - 1)
  const end = Math.min(totalPages, current + 1)

  for (let page = start; page <= end; page += 1) {
    pages.push(page)
  }

  if (!pages.includes(1)) pages.unshift(1)
  if (!pages.includes(totalPages)) pages.push(totalPages)

  return [...new Set(pages)].sort((left, right) => left - right)
})

const resetFilters = () => {
  searchQuery.value = ''
  activeStatusFilter.value = 'all'
  activeSeverityFilter.value = 'all'
  activeMacFilter.value = 'all'
  activeSideFilter.value = 'all'
  currentPage.value = 1
  activeMenuId.value = ''
  activeFilterMenu.value = ''
}

const setStatusFilter = (value) => {
  activeStatusFilter.value = value
  activeFilterMenu.value = ''
}

const setSeverityFilter = (value) => {
  activeSeverityFilter.value = value
  activeFilterMenu.value = ''
}

const setDeviceFilter = (value) => {
  activeMacFilter.value = value
  activeFilterMenu.value = ''
}

const setSideFilter = (value) => {
  activeSideFilter.value = value
  activeFilterMenu.value = ''
}

const toggleFilterMenu = (name) => {
  activeFilterMenu.value = activeFilterMenu.value === name ? '' : name
  activeMenuId.value = ''
}

const goToPage = (page) => {
  currentPage.value = Math.min(Math.max(page, 1), pageCount.value)
}

const previousPage = () => {
  goToPage(currentPage.value - 1)
}

const nextPage = () => {
  goToPage(currentPage.value + 1)
}

const toggleAlertMenu = (alertId) => {
  if (!alertId) return
  activeMenuId.value = activeMenuId.value === alertId ? '' : alertId
  activeFilterMenu.value = ''
}

const closeAlertMenu = (event) => {
  if (
    event?.target?.closest?.('.row-actions')
    || event?.target?.closest?.('.severity-control')
    || event?.target?.closest?.('.status-control')
  ) return
  activeMenuId.value = ''
  activeFilterMenu.value = ''
}

const copyToClipboard = async (value) => {
  try {
    await navigator.clipboard.writeText(String(value || '').trim())
  } catch (error) {
    console.error('Error copying alert value:', error)
  } finally {
    activeMenuId.value = ''
  }
}

const confirmClearHistory = async () => {
  try {
    await healthStore.clearAllAlerts()
    healthStore.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Alert history cleared.' }
  } catch {
    healthStore.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Could not clear history.' }
  } finally {
    pendingClearHistory.value = false
  }
}

const confirmDeleteAlert = async (alertId) => {
  try {
    await healthStore.deleteAlert(alertId)
    healthStore.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Alert deleted.' }
  } catch {
    healthStore.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Could not delete alert.' }
  } finally {
    pendingDeleteAlertId.value = null
    activeMenuId.value = ''
  }
}

const toggleAlertStatus = async (alert) => {
  const nextStatus = alert.status === 'READ' ? 'PENDING' : 'READ'
  try {
    await healthStore.setAlertStatus(alert.id, nextStatus)
    healthStore.lastToast = {
      id: Date.now(),
      sensor: 'SYSTEM',
      message: nextStatus === 'READ' ? 'Alert marked as read.' : 'Alert marked as pending.'
    }
  } catch {
    healthStore.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Could not update alert status.' }
  } finally {
    activeMenuId.value = ''
  }
}

const refreshAlerts = async () => {
  if (isRefreshing.value) return

  isRefreshing.value = true
  try {
    await healthStore.fetchAlertHistory()
    lastRefreshedAt.value = new Date()
  } finally {
    isRefreshing.value = false
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    activeMenuId.value = ''
    activeFilterMenu.value = ''
    pendingDeleteAlertId.value = null
  }
}

watch(
  [searchQuery, activeStatusFilter, activeSeverityFilter, activeMacFilter, activeSideFilter],
  () => {
    currentPage.value = 1
    activeMenuId.value = ''
    activeFilterMenu.value = ''
  }
)

onMounted(async () => {
  await Promise.all([
    healthStore.fetchAlertHistory(),
    healthStore.fetchDeviceInventory()
  ])
  lastRefreshedAt.value = new Date()
  document.addEventListener('click', closeAlertMenu)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeAlertMenu)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.alerts-page { min-height: 100%; }
.page-shell { display: flex; flex-direction: column; gap: 22px; max-width: 1440px; margin: 0 auto; padding-bottom: 12px; }
.page-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.page-eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.68rem; font-weight: 900; color: #2559bd; }
.page-title { margin: 0; font-size: clamp(2rem, 3vw, 2.8rem); font-weight: 900; letter-spacing: -0.05em; color: var(--text-main); }
.material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; vertical-align: middle; }
.action-button .material-symbols-outlined, .summary-icon .material-symbols-outlined, .search-icon, .icon-button .material-symbols-outlined, .empty-icon .material-symbols-outlined { font-size: 1rem; }
.search-icon { font-size: 1.1rem; }
.page-actions .material-symbols-outlined { font-size: 1.05rem; }
.page-subtitle { margin: 8px 0 0; font-size: 0.95rem; line-height: 1.6; color: var(--text-muted); }
.page-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.refresh-meta { display: flex; flex-direction: column; gap: 2px; padding: 8px 10px; border-radius: 14px; background: var(--surface-panel-strong); border: 1px solid var(--surface-border); box-shadow: 0 14px 32px var(--surface-shadow); }
.refresh-meta__label { font-size: 0.62rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.refresh-meta__value { font-size: 0.76rem; font-weight: 800; color: var(--text-main); }
.action-button { display: inline-flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 16px; border: 1px solid transparent; font-weight: 900; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease; }
.action-button:hover { transform: translateY(-1px); }
.action-button:disabled { opacity: 0.7; cursor: progress; transform: none; }
.action-button--ghost { background: var(--surface-panel-strong); color: var(--text-main); border-color: var(--surface-border); box-shadow: 0 8px 20px var(--surface-shadow); }
.action-button--danger { background: rgba(239, 68, 68, 0.08); color: #b91c1c; border-color: rgba(239, 68, 68, 0.14); }
.summary-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.summary-card { padding: 22px; border-radius: 24px; border: 1px solid var(--surface-border); background: var(--surface-card); box-shadow: 0 14px 34px var(--surface-shadow); }
.summary-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.summary-icon { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; }
.summary-icon span { font-size: 1.2rem; }
.summary-icon--blue { color: #2559bd; background: rgba(37, 89, 189, 0.1); }
.summary-icon--red { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.summary-icon--teal { color: #047857; background: rgba(16, 185, 129, 0.1); }
.summary-label { font-size: 0.68rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.summary-value { display: block; margin: 0; font-size: clamp(1.9rem, 3vw, 2.7rem); font-weight: 900; letter-spacing: -0.05em; color: var(--text-main); line-height: 1; }
.summary-note { margin: 8px 0 0; color: var(--text-muted); font-size: 0.92rem; line-height: 1.5; }
.filters-card { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding: 14px; border-radius: 22px; border: 1px solid var(--border-color); background: var(--surface-panel); box-shadow: 0 14px 30px var(--surface-shadow); }
.search-wrap { position: relative; flex: 1 1 320px; min-width: 260px; }
.search-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: rgba(100, 116, 139, 0.7); }
.search-input { width: 100%; padding: 13px 16px 13px 46px; border-radius: 18px; border: 1px solid var(--surface-border); background: var(--surface-panel-strong); color: var(--text-main); font-weight: 700; box-sizing: border-box; outline: none; }
.search-input::placeholder { color: var(--text-muted); }
.status-control { position: relative; min-width: 180px; }
.segment-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.severity-control { position: relative; min-width: 180px; }
.severity-button { width: 100%; display: inline-flex; align-items: center; justify-content: space-between; gap: 10px; padding: 13px 16px; border-radius: 18px; border: 1px solid var(--surface-border); background: var(--surface-panel-strong); color: var(--text-main); font-size: 0.72rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; cursor: pointer; box-sizing: border-box; transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; }
.severity-button:hover { transform: translateY(-1px); box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04); }
.severity-button__value { color: #2559bd; }
.severity-button__icon { font-size: 1.05rem; color: #64748b; }
.severity-menu { position: absolute; top: calc(100% + 8px); left: 0; z-index: 25; width: 100%; padding: 8px; border-radius: 18px; border: 1px solid var(--surface-border); background: var(--surface-card); box-shadow: 0 22px 44px var(--surface-shadow); }
.severity-menu-item { width: 100%; padding: 11px 12px; border: 0; border-radius: 12px; background: transparent; color: var(--text-main); font-size: 0.82rem; font-weight: 800; cursor: pointer; text-align: left; transition: background 0.2s ease, color 0.2s ease; }
.severity-menu-item:hover { background: rgba(37, 89, 189, 0.08); color: #2559bd; }
.severity-menu-item--active { background: rgba(37, 89, 189, 0.1); color: #2559bd; }
.result-chip { padding: 11px 14px; border-radius: 14px; background: var(--surface-panel-strong); color: var(--text-muted); font-size: 0.72rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; border: 1px solid var(--surface-border); }
.table-card { overflow: hidden; border-radius: 24px; border: 1px solid var(--border-color); background: var(--surface-card); box-shadow: 0 18px 40px var(--surface-shadow); }
.table-wrap { overflow-x: auto; }
.alerts-table { width: 100%; min-width: 1140px; border-collapse: separate; border-spacing: 0; }
.alerts-table th { padding: 16px 18px; text-align: left; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; background: var(--surface-panel-strong); border-bottom: 1px solid var(--surface-border); }
.alerts-table td { padding: 18px; vertical-align: top; border-bottom: 1px solid rgba(148, 163, 184, 0.1); color: var(--text-main); }
.alerts-table tbody tr:hover { background: var(--surface-card-soft); }
.align-right { text-align: right; }
.primary-cell { font-size: 0.92rem; font-weight: 800; color: var(--text-main); }
.secondary-cell { margin-top: 3px; font-size: 0.72rem; color: var(--text-muted); }
.mac-chip, .sensor-chip, .severity-chip, .status-chip { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 6px 10px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; }
.device-cell { display: flex; flex-direction: column; gap: 6px; }
.device-name { font-size: 0.92rem; font-weight: 900; color: var(--text-main); }
.mac-chip { font-family: 'Inter', sans-serif; color: #2559bd; background: rgba(37, 89, 189, 0.08); }
.sensor-chip { border: 1px solid transparent; }
.sensor-chip--blue { color: #2559bd; background: rgba(37, 89, 189, 0.08); border-color: rgba(37, 89, 189, 0.14); }
.sensor-chip--teal { color: #047857; background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.12); }
.sensor-chip--amber { color: #b45309; background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.14); }
.sensor-chip--neutral { color: #475569; background: rgba(148, 163, 184, 0.12); border-color: rgba(148, 163, 184, 0.14); }
.side-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 78px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border: 1px solid transparent;
}
.side-chip--active {
  color: #2559bd;
  background: rgba(37, 89, 189, 0.08);
  border-color: rgba(37, 89, 189, 0.14);
}
.side-chip--neutral {
  color: #475569;
  background: rgba(148, 163, 184, 0.12);
  border-color: rgba(148, 163, 184, 0.14);
}
.message-cell { margin: 0; max-width: 520px; font-size: 0.92rem; line-height: 1.5; color: var(--text-main); }
.status-chip--pending { color: #b45309; background: rgba(245, 158, 11, 0.14); }
.status-chip--read { color: #047857; background: rgba(16, 185, 129, 0.14); }
.status-dot { width: 8px; height: 8px; border-radius: 999px; background: currentColor; opacity: 0.9; }
.severity-chip--critical { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.severity-chip--warning { color: #b45309; background: rgba(245, 158, 11, 0.14); }
.severity-chip--info { color: #2559bd; background: rgba(37, 89, 189, 0.08); }
.row-actions { position: relative; display: inline-flex; align-items: center; gap: 6px; }
.icon-button { width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid var(--surface-border); background: var(--surface-panel-strong); color: #475569; cursor: pointer; transition: color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; }
.icon-button:hover { color: #2559bd; border-color: rgba(37, 89, 189, 0.24); box-shadow: 0 10px 18px rgba(37, 89, 189, 0.08); transform: translateY(-1px); }
.context-menu { position: absolute; top: calc(100% + 8px); right: 0; z-index: 30; min-width: 220px; padding: 8px; border-radius: 18px; border: 1px solid var(--surface-border); background: var(--surface-card); box-shadow: 0 22px 44px var(--surface-shadow); }
.context-menu-item { width: 100%; display: flex; align-items: center; gap: 10px; padding: 11px 12px; border: 0; border-radius: 12px; background: transparent; color: var(--text-main); font-size: 0.82rem; font-weight: 800; cursor: pointer; text-align: left; transition: background 0.2s ease, color 0.2s ease; }
.context-menu-item:hover { background: rgba(37, 89, 189, 0.08); color: #2559bd; }
.context-menu-item--danger:hover { background: rgba(239, 68, 68, 0.1); color: #dc2626; }
.context-menu-item .material-symbols-outlined { font-size: 1rem; }
.context-menu-confirm { padding: 8px 12px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.context-confirm-label { font-size: 0.78rem; font-weight: 800; color: #dc2626; text-align: center; }
.context-confirm-actions { display: flex; gap: 6px; justify-content: center; }
.confirm-label { font-size: 0.78rem; font-weight: 800; color: #dc2626; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 24px; text-align: center; }
.empty-icon { width: 80px; height: 80px; border-radius: 999px; display: grid; place-items: center; background: var(--surface-panel-strong); color: rgba(100, 116, 139, 0.85); margin-bottom: 18px; border: 1px solid var(--surface-border); }
.empty-icon span { font-size: 2.4rem; }
.empty-state h2 { margin: 0; font-size: 1.2rem; font-weight: 900; color: var(--text-main); }
.empty-state p { margin: 8px 0 0; max-width: 420px; color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }
.empty-action { margin-top: 22px; padding: 12px 16px; border: 1px solid rgba(37, 89, 189, 0.16); border-radius: 14px; background: rgba(37, 89, 189, 0.12); color: #2559bd; font-weight: 900; cursor: pointer; }
.table-footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; padding: 16px 18px; border-top: 1px solid var(--surface-border); background: var(--surface-panel); }
.footer-text { margin: 0; color: var(--text-muted); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; }
.pagination { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.page-button, .page-number { padding: 10px 14px; border-radius: 12px; border: 1px solid var(--surface-border); background: var(--surface-panel-strong); color: #475569; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; cursor: pointer; transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease; }
.page-button:hover:not(:disabled), .page-number:hover { background: rgba(37, 89, 189, 0.08); color: #2559bd; transform: translateY(-1px); }
.page-button:disabled { opacity: 0.45; cursor: not-allowed; }
.page-number--active { background: #2559bd; color: #ffffff; border-color: transparent; }
@media (max-width: 1100px) { .summary-grid { grid-template-columns: 1fr; } .filters-card { align-items: stretch; } .search-wrap { flex-basis: 100%; } }
@media (max-width: 900px) { .page-header { align-items: flex-start; } .page-actions { width: 100%; justify-content: flex-start; } }
@media (max-width: 768px) {
  .filters-card { padding: 12px; }
  .status-control, .severity-control { width: 100%; }
  .segment-button { flex: 1 1 140px; justify-content: center; }
  .table-footer { align-items: flex-start; }
  .pagination { width: 100%; }
  .alerts-table { min-width: 1020px; }
}

</style>
