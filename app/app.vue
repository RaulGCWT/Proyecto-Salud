<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

// --- STATE ---
const heartRate = ref(72);
const respiratoryRate = ref(16);
const hrv = ref(45);
const isOccupied = ref(true);
const alertHistory = ref([]);

// --- REAL-WORLD THRESHOLDS (Logic) ---

// 1. Heart Rate: Normal resting is 60-100 BPM.
const isHRAlert = computed(() => heartRate.value > 100 || heartRate.value < 50);

// 2. Respiratory Rate: Normal at rest is 12-20 RPM.
const isRespAlert = computed(() => respiratoryRate.value > 20 || respiratoryRate.value < 10);

// 3. HRV: Below 20ms is often a sign of high physiological stress or illness.
const isHRVAlert = computed(() => hrv.value < 20);

// --- FUNCTIONS ---
const updateSensors = () => {
  // Simulating realistic fluctuations
  heartRate.value = Math.floor(Math.random() * (115 - 45 + 1)) + 45;
  respiratoryRate.value = Math.floor(Math.random() * (25 - 8 + 1)) + 8;
  hrv.value = Math.floor(Math.random() * (80 - 15 + 1)) + 15;

  checkAlerts();
};

const checkAlerts = () => {
  const now = new Date().toLocaleTimeString();
  
  if (isHRAlert.value) {
    addAlert(now, 'Heart Rate', `Out of range: ${heartRate.value} BPM`, 'Critical');
  }
  if (isRespAlert.value) {
    addAlert(now, 'Resp. Rate', `Abnormal breathing: ${respiratoryRate.value} RPM`, 'Warning');
  }
  if (isHRVAlert.value) {
    addAlert(now, 'HRV', `Very low variability: ${hrv.value} ms`, 'Warning');
  }
};

const addAlert = (time, sensor, message, level) => {
  alertHistory.value.unshift({ time, sensor, message, level });
  if (alertHistory.value.length > 5) alertHistory.value.pop();
};

let dataInterval;
onMounted(() => { dataInterval = setInterval(updateSensors, 3000); });
onUnmounted(() => { clearInterval(dataInterval); });
</script>

<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">⚡</div>
        <div class="logo-text"><h2>WELLTECH</h2><span>IoT Health</span></div>
      </div>
      <nav class="sidebar-nav">
        <a href="#" class="nav-item active">📊 Dashboard</a>
        <a href="#" class="nav-item">🛏️ Mattresses</a>
        <a href="#" class="nav-item">⚠️ Alerts</a>
        <a href="#" class="nav-item">🕒 History</a>
      </nav>
    </aside>

    <main class="content-area">
      <header class="main-header">
        <h1>Live Sensor Monitoring</h1>
        <p>Real-time clinical thresholds for smart mattresses</p>
      </header>

      <section class="sensor-grid">
        <DashboardCard 
          type="hr" 
          title="Heart Rate" 
          :main-text="`${heartRate} BPM`" 
          :description="isHRAlert ? 'Abnormal Heart Rate' : 'Normal'"
          :is-alert="isHRAlert" 
        />

        <DashboardCard 
          type="hrv" 
          title="HR Variability" 
          :main-text="`${hrv} ms`" 
          :description="isHRVAlert ? 'High Stress Detected' : 'Good Recovery'"
          :is-alert="isHRVAlert"
        />
        
        <DashboardCard 
          type="resp" 
          title="Resp. Rate" 
          :main-text="`${respiratoryRate} RPM`" 
          :description="isRespAlert ? 'Irregular Breathing' : 'Normal'"
          :is-alert="isRespAlert"
        />
        
        <DashboardCard 
          type="presence" 
          title="Bed Status" 
          :main-text="isOccupied ? 'In Use' : 'Empty'" 
          description="Occupancy Sensor"
          :is-alert="false"
        />
      </section>

      <section class="table-container">
        <h3>Live Alert Log</h3>
        <table class="custom-table">
          <thead>
            <tr><th>Time</th><th>Sensor</th><th>Message</th><th>Level</th></tr>
          </thead>
          <tbody>
            <tr v-for="(alert, index) in alertHistory" :key="index">
              <td>{{ alert.time }}</td>
              <td>{{ alert.sensor }}</td>
              <td>{{ alert.message }}</td>
              <td><span :class="['badge', alert.level === 'Critical' ? 'badge-error' : 'badge-warn']">{{ alert.level }}</span></td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<style>
/* Base Styles */
body { margin: 0; font-family: 'Inter', sans-serif; background-color: #f8fafc; }
.dashboard-wrapper { display: flex; }
.sidebar { width: 260px; background: #0f172a; color: white; height: 100vh; position: fixed; }
.sidebar-header { padding: 24px; background: #020617; display: flex; align-items: center; gap: 12px; }
.logo-icon { background: #3b82f6; width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.sidebar-nav { padding: 20px 0; }
.nav-item { display: block; padding: 12px 24px; color: #94a3b8; text-decoration: none; }
.nav-item.active { border-left: 4px solid #3b82f6; background: #1e293b; color: white; }
.content-area { margin-left: 260px; width: calc(100% - 260px); padding: 40px; }
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin: 32px 0; }
.table-container { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.custom-table { width: 100%; border-collapse: collapse; }
.custom-table th, .custom-table td { text-align: left; padding: 12px; border-bottom: 1px solid #f1f5f9; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-error { background: #fee2e2; color: #ef4444; }
.badge-warn { background: #fef3c7; color: #d97706; }
</style>