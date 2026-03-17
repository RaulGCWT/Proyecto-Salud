<template>
  <div class="alerts-page">
    <header class="main-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">Alert History</h1>
          <h3 class="subtitle">Critical records stored in DynamoDB</h3>
        </div>
        <button @click="healthStore.clearAllAlerts()" class="btn-clear">🗑️ Clear History</button>
      </div>
    </header>

    <div class="filters-bar shadow-sm">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" type="text" placeholder="Search by MAC, sensor, or message..." />
      </div>
      <div class="results-count">Showing {{ filteredAlerts.length }} alerts</div>
    </div>

    <div class="table-container shadow-sm">
      <table v-if="filteredAlerts.length > 0">
        <thead>
          <tr>
            <th>Time</th>
            <th>Device (MAC)</th>
            <th>Sensor</th>
            <th>Message</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in filteredAlerts" :key="alert.id">
            <td>{{ alert.time }}</td>
            <td><code class="mac-badge">{{ alert.mac }}</code></td>
            <td><span class="badge">{{ alert.sensor }}</span></td>
            <td>{{ alert.message }}</td>
            <td><span class="level-tag critical">{{ alert.level }}</span></td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🔔</div>
        <p v-if="searchQuery">No alerts match your search "{{ searchQuery }}"</p>
        <p v-else>No alerts recorded in the database.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHealthStore } from '~/stores/health'

const healthStore = useHealthStore()
const searchQuery = ref('')

const filteredAlerts = computed(() => {
  const history = healthStore.alertHistory
  if (!searchQuery.value) return history
  const query = searchQuery.value.toLowerCase()
  return history.filter(alert => (
    alert.mac?.toLowerCase().includes(query) ||
    alert.sensor?.toLowerCase().includes(query) ||
    alert.message?.toLowerCase().includes(query)
  ))
})

onMounted(async () => { await healthStore.fetchAlertHistory() })
</script>

<style scoped>
.alerts-page { padding: 2rem; }
.main-header { margin-bottom: 2rem; }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 1.8rem; font-weight: 800; color: var(--text-main, #0f172a); margin: 0; }
.subtitle { color: #64748b; font-size: 1rem; margin-top: 4px; }
.btn-clear { background: #ef4444; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-clear:hover { background: #dc2626; }
.filters-bar { background: white; padding: 16px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.search-box { display: flex; align-items: center; background: #f1f5f9; padding: 8px 16px; border-radius: 8px; width: 400px; }
.search-box input { background: transparent; border: none; margin-left: 10px; width: 100%; outline: none; color: #334155; }
.results-count { color: #64748b; font-size: 0.9rem; font-weight: 500; }
.table-container { background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
table { width: 100%; border-collapse: collapse; }
th { background: #f8fafc; padding: 16px; text-align: left; font-size: 0.85rem; text-transform: uppercase; color: #64748b; border-bottom: 2px solid #e2e8f0; }
td { padding: 16px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.mac-badge { background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-family: monospace; color: #2563eb; }
.badge { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.level-tag.critical { color: #ef4444; font-weight: 800; }
.empty-state { padding: 60px; text-align: center; color: #94a3b8; }
.empty-icon { font-size: 3rem; margin-bottom: 10px; }
.dark-mode .table-container, .dark-mode .filters-bar { background: #1e293b; border-color: #334155; }
.dark-mode th { background: #0f172a; color: #94a3b8; }
.dark-mode td { color: #e2e8f0; border-color: #334155; }
.dark-mode .search-box { background: #0f172a; }
.dark-mode .search-box input { color: white; }
</style>