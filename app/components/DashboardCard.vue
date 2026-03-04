<template>
  <div class="card" :class="['type-' + type, { 'card-alert': isAlert }]">
    <span class="card-label">{{ title }}</span>
    <div class="card-value">
      {{ mainText }}
    </div>
    <div class="card-indicator" :class="isAlert ? 'status-error' : 'status-ok'">
      {{ description }}
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
// --- REACTIVE STATE (English variables) ---
const heartRate = ref(72);
const respiratoryRate = ref(16);
const hrv = ref(45); // Initial value in ms
const isOccupied = ref(true);
const alertHistory = ref([
  { time: '12:30:15', sensor: 'Heart Rate', message: 'Spike detected: 105 BPM', level: 'Critical' },
  { time: '09:12:04', sensor: 'Movement', message: 'Prolonged absence (1h)', level: 'Warning' }
]);



const props=defineProps({
  title:String,
  mainText:String,
  description:String,
  type: 'bpm' | 'hrv' | 'rpm' | 'sts'
})
</script>

<style scoped>
/* Base card style */
.card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s;
  border-left: 5px solid #cbd5e1; /* Default neutral border */
}

/* Specific styles per TYPE */
.type-hr { border-left-color: #ef4444; }
.type-hr .card-value { color: #ef4444; }

.type-hrv { border-left-color: #06b6d4; } /* Cyan/Teal border */
.type-hrv .card-value { color: #06b6d4; }

.type-resp { border-left-color: #8b5cf6; }
.type-resp .card-value { color: #8b5cf6; }

.type-presence { border-left-color: #10b981; }
.type-presence .card-value { color: #10b981; }

/* Text styling */
.card-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.card-value { font-size: 2.2rem; font-weight: 800; margin: 12px 0; }
.card-indicator { font-size: 0.85rem; font-weight: 500; }

.status-ok { color: #10b981; }
.status-error { color: #ef4444; font-weight: bold; }

/* Critical alert animation */
.card-alert { 
  background-color: #fff1f0; 
  animation: pulse 2s infinite; 
  border: 2px solid #ef4444;
  
}

@keyframes pulse { 
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
</style>
