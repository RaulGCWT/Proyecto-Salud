<template>
  <div>
    <header class="main-header">
      <h1>Health Alerts Log</h1>
      <p>Historical events detected by sensors</p>
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
.table-container { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.custom-table { width: 100%; border-collapse: collapse; }
.custom-table th, .custom-table td { text-align: left; padding: 12px; border-bottom: 1px solid #f1f5f9; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-error { background: #fee2e2; color: #ef4444; }
.badge-warn { background: #fef3c7; color: #d97706; }
</style>