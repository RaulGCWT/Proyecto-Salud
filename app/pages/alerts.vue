<template>
  <div class="alerts-page">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h1>Historial de Alertas (DynamoDB)</h1>
      <button @click="healthStore.clearAllAlerts()" style="background: #ef4444; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; font-weight: bold;">
        🗑️ Borrar todo
      </button>
    </div>
    
    <div class="table-container">
      <table v-if="healthStore.alertHistory.length > 0">
        <thead>
          <tr>
            <th>Hora</th>
            <th>Sensor</th>
            <th>Mensaje</th>
            <th>Nivel</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in healthStore.alertHistory" :key="alert.id">
            <td>{{ alert.time }}</td>
            <td><span class="badge">{{ alert.sensor }}</span></td>
            <td>{{ alert.message }}</td>
            <td class="critical">{{ alert.level }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        No hay alertas registradas en la base de datos.
      </div>
    </div>
  </div>
</template>

<script setup>
import { useHealthStore } from '~/stores/health'
import { onMounted } from 'vue'

const healthStore = useHealthStore()

onMounted(async () => {
  // Al cargar la página, pedimos los datos reales al Backend
  await healthStore.fetchAlertHistory()
})
</script>

<style scoped>
.alerts-page { padding: 2rem; }
.table-container { margin-top: 1.5rem; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: 1rem; border-bottom: 1px solid #eee; }
th { background: #f8fafc; font-weight: bold; }
.badge { background: #e2e8f0; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.critical { color: #ef4444; font-weight: bold; }
.empty-state { padding: 3rem; text-align: center; color: #64748b; }
</style>