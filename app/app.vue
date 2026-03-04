<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">
          <h2>WELLTECH</h2>

          <span>IoT Health</span>
        </div>
      </div>
      

      <nav class="sidebar-nav">
        <a href="#" class="nav-item active">📊 Dashboard</a>
        <a href="#" class="nav-item">🛏️ Mattresses</a>
        <a href="#" class="nav-item">⚠️ Alerts</a>
        <a href="#" class="nav-item">🕒 History</a>
      </nav>

      <div class="sidebar-footer">
        <p><strong>Admin_Health</strong></p>
        <button class="btn-logout">Logout</button>
      </div>
    </aside>

    <main class="content-area">
      <header class="main-header">
        <h1>Live Sensor Monitoring</h1>
        <p>Real-time status of smart mattresses</p>
      </header>

      <section class="sensor-grid">
        <div class="card" :class="{ 'card-alert': isHeartRateHigh }">
          <span class="card-label">Heart Rate</span>
          <div class="card-value heart-color">
            {{ heartRate }} <small>BPM</small>
          </div>
          <div class="card-indicator" :class="isHeartRateHigh ? 'status-error' : 'status-ok'">
            {{ isHeartRateHigh ? 'Critical: High HR' : 'Normal' }}
          </div>
        </div>
        
        <!-- <div class="card card-resp">
          <span class="card-label">Resp. Rate</span>
          <div class="card-value resp-color">
            {{ respiratoryRate }} <small>RPM</small>
          </div>
          <div class="card-indicator status-ok">Normal</div>
        </div> -->
        
        <DashboardCard type="hr" title="Resp. Rate" :main-text="`${respiratoryRate} RPM`" description="Normal"/>
        <DashboardCard title="Bed status" :main-text=" isOccupied ? 'In Use' : 'Empty' " :description="isOccupied ? 'User Detected' : 'No Presence'"/>
        
        <!-- <div class="card card-presence">
        <!-- <div class="card card-presence">
          <span class="card-label">Bed Status</span>
          <div class="card-value presence-color">
            {{ isOccupied ? 'In Use' : 'Empty' }}
          </div>
          <div class="card-indicator status-ok">
            {{ isOccupied ? 'User Detected' : 'No Presence' }}
          </div>
        </div> -->
      </section>

      <section class="table-container">
        <h3>Recent Health Alerts (Last 24h)</h3>
        <table class="custom-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Sensor</th>
              <th>Message</th>
              <th>Level</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(alert, index) in alertHistory" :key="index">
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
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

// --- REACTIVE STATE (English variables) ---
const heartRate = ref(72);
const respiratoryRate = ref(16);
const isOccupied = ref(true);
const alertHistory = ref([
  { time: '12:30:15', sensor: 'Heart Rate', message: 'Spike detected: 105 BPM', level: 'Critical' },
  { time: '09:12:04', sensor: 'Movement', message: 'Prolonged absence (1h)', level: 'Warning' }
]);

// --- COMPUTED PROPERTIES ---
const isHeartRateHigh = computed(() => heartRate.value > 100);

// --- FUNCTIONS ---
const updateSensors = () => {
  // Simulate random sensor fluctuation
  heartRate.value = Math.floor(Math.random() * (110 - 60 + 1)) + 60;
  respiratoryRate.value = Math.floor(Math.random() * (22 - 12 + 1)) + 12;

  // Add a new alert if heart rate is critical
  if (heartRate.value > 100) {
    const now = new Date().toLocaleTimeString();
    alertHistory.value.unshift({
      time: now,
      sensor: 'Heart Rate',
      message: `Critical value: ${heartRate.value} BPM`,
      level: 'Critical'
    });
    
    // Keep only the last 5 alerts for display
    if (alertHistory.value.length > 5) alertHistory.value.pop();
  }
};

// --- LIFECYCLE HOOKS ---
let dataInterval;
onMounted(() => {
  dataInterval = setInterval(updateSensors, 3000); // Updates every 3 seconds
});

onUnmounted(() => {
  clearInterval(dataInterval);
});
</script>

<style>
/* 1. RESET AND BASE */
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
.dashboard-wrapper { display: flex; }

/* 2. SIDEBAR */
.sidebar {
  width: 260px; background-color: #0f172a; color: white; height: 100vh;
  position: fixed; left: 0; top: 0; display: flex; flex-direction: column; z-index: 100;
}
.sidebar-header { padding: 24px; display: flex; align-items: center; gap: 12px; background-color: #020617; }
.logo-icon { background: #3b82f6; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; }
.sidebar-nav { flex: 1; padding: 20px 0; }
.nav-item { display: block; padding: 12px 24px; color: #94a3b8; text-decoration: none; }
.nav-item.active { border-left: 4px solid #3b82f6; background-color: #1e293b; color: white; }

/* 3. CONTENT AREA */
.content-area { margin-left: 260px; width: calc(100% - 260px); padding: 40px; min-height: 100vh; }

/* 4. CARDS AND ALERTS */
.sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin: 32px 0; }
.card { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.3s; }

/* Alert state for the card */
.card-alert { border: 2px solid #ef4444; background-color: #fff1f0; animation: pulse 2s infinite; }
@keyframes pulse { 
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.card-value { font-size: 2.2rem; font-weight: 800; margin: 12px 0; }
.heart-color { color: #ef4444; }
.resp-color { color: #8b5cf6; }
.presence-color { color: #10b981; }

.status-ok { color: #10b981; }
.status-error { color: #ef4444; font-weight: bold; }

/* 5. TABLE */
.table-container { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.custom-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
.custom-table th, .custom-table td { text-align: left; padding: 12px; border-bottom: 1px solid #f1f5f9; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-error { background: #fee2e2; color: #ef4444; }
.badge-warn { background: #fef3c7; color: #d97706; }
</style>