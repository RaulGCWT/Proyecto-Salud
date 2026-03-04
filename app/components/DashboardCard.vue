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
// Props definition including the missing isAlert boolean
const props = defineProps({
  title: String,
  mainText: String,
  description: String,
  isAlert: Boolean,
  type: 'hr' | 'hrv' | 'resp' | 'presence' // Supported: 'hr' | 'hrv' | 'resp' | 'presence'
})
</script>

<style scoped>
.card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s;
  border-left: 5px solid #cbd5e1;
  position: relative;
}

/* Color coding by sensor type */
.type-hr { border-left-color: #ef4444; }
.type-hr .card-value { color: #ef4444; }

.type-hrv { border-left-color: #06b6d4; }
.type-hrv .card-value { color: #06b6d4; }

.type-resp { border-left-color: #8b5cf6; }
.type-resp .card-value { color: #8b5cf6; }

.type-presence { border-left-color: #10b981; }
.type-presence .card-value { color: #10b981; }

.card-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.card-value { font-size: 2.2rem; font-weight: 800; margin: 12px 0; }
.card-indicator { font-size: 0.85rem; font-weight: 500; }

.status-ok { color: #10b981; }
.status-error { color: #ef4444; font-weight: bold; }

/* PULSE ANIMATION: Fixed to apply to border and shadow */
.card-alert { 
  background-color: #fff1f0 !important; 
  border: 2px solid #ef4444 !important;
  animation: pulse-animation 2s infinite; 
}

@keyframes pulse-animation { 
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
</style>