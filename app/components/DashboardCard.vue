<template>
  <div class="card" :class="['type-' + type, { 'card-alert': isAlert }]">
    <span class="card-label">{{ title }}</span>
    <div class="card-value" :class="colorClass">
      {{ mainText }}
    </div>
    <div class="card-indicator" :class="isAlert ? 'status-error' : 'status-ok'">
      {{ description }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({
  title: String,
  mainText: String,
  description: String,
  isAlert: Boolean,
  type: String
});

const colorClass = computed(() => {
  if (props.type === 'hr') return 'heart-color';
  if (props.type === 'resp') return 'resp-color';
  if (props.type === 'presence') return 'presence-color';
  return '';
});
</script>

<style scoped>
.card {
  background: white; padding: 24px; border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.3s;
  border-left: 5px solid #cbd5e1;
}
.type-hr { border-left-color: #ef4444; }
.type-hrv { border-left-color: #06b6d4; }
.type-resp { border-left-color: #8b5cf6; }
.type-presence { border-left-color: #10b981; }

.card-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.card-value { font-size: 2.2rem; font-weight: 800; margin: 12px 0; }

.heart-color { color: #ef4444; }
.resp-color { color: #8b5cf6; }
.presence-color { color: #10b981; }

.status-ok { color: #10b981; }
.status-error { color: #ef4444; font-weight: bold; }

.card-alert { 
  background-color: #fff1f0; border: 2px solid #ef4444;
  animation: pulse 2s infinite; 
}
@keyframes pulse { 
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
</style>