<template>
  <div>
    <header class="main-header">
      <h1 class="page-title">Health Alerts Log</h1>
      <p class="page-subtitle">Historical events detected by sensors</p>
    </header>

    <section class="table-container">
      <table class="custom-table">
        <thead>
          <tr><th>Time</th><th>Sensor</th><th>Message</th><th>Level</th></tr>
        </thead>
        <tbody>
          <tr v-for="(alert, index) in health.alertHistory" :key="index">
            <td>{{ alert.time }}</td>
            <td>{{ alert.sensor }}</td>
            <td>{{ alert.message }}</td>
            <td>
              <span :class="['badge', alert.level === 'Critical' ? 'badge-error' : 'badge-warn']">
                {{ alert.level }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { useHealthStore } from '~/stores/health'
const health = useHealthStore()
</script>

<style scoped>
.page-title { color: var(--text-main); margin: 0; }
.page-subtitle { color: var(--text-muted); margin: 5px 0 20px 0; }

.table-container { 
  background: var(--bg-card); 
  padding: 24px; 
  border-radius: 16px; 
  box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
  border: 1px solid var(--border-color);
}

.custom-table { width: 100%; border-collapse: collapse; color: var(--text-main); }
.custom-table th { text-align: left; padding: 12px; border-bottom: 2px solid var(--border-color); color: var(--text-muted); }
.custom-table td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border-color); }

.badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
.badge-error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.badge-warn { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
</style>