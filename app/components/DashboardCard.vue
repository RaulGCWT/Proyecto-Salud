<template>
  <div 
    class="card" 
    :class="[
      'type-' + type, 
      { 'card-alert': isAlert },
      { 'is-empty': type === 'presence' && mainText === 'Empty' }
    ]"
  >
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
import { computed } from 'vue'

const props = defineProps({ 
  title: String, 
  mainText: String, 
  description: String, 
  isAlert: Boolean, 
  type: String 
});

const colorClass = computed(() => {
  if (props.type === 'hr') return 'heart-color';
  if (props.type === 'hrv') return 'hrv-color';
  if (props.type === 'resp') return 'resp-color';
  if (props.type === 'presence') return 'presence-color';
  return '';
});
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
  overflow: hidden;
}

/* Bordes de color por tipo */
.type-hr { border-left-color: #ef4444; }
.type-hrv { border-left-color: #06b6d4; }
.type-resp { border-left-color: #8b5cf6; }
.type-presence { border-left-color: #10b981; }

.card-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.card-value { font-size: 2rem; font-weight: 800; margin: 8px 0; }

/* Colores de texto */
.heart-color { color: #ef4444; }
.hrv-color { color: #06b6d4; }
.resp-color { color: #8b5cf6; }
.presence-color { color: #10b981; }

.card-indicator { font-size: 0.85rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; display: inline-block; }
.status-ok { background: #dcfce7; color: #166534; }
.status-error { background: #fee2e2; color: #991b1b; }

/* --- EFECTO PULSO DE ALERTA --- */
.card-alert {
  border-left-color: #b91c1c !important;
  animation: pulse-red 1.5s infinite;
}

@keyframes pulse-red {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    background-color: white;
  }
  50% {
    box-shadow: 0 0 0 15px rgba(239, 68, 68, 0);
    background-color: #fef2f2; /* Un tono rojizo muy suave */
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    background-color: white;
  }
}

/* ESTILO CAMA VACÍA */
.is-empty {
  background-color: #f1f5f9 !important;
  border-left-color: #94a3b8 !important;
  opacity: 0.8;
}
.is-empty .presence-color {
  color: #64748b !important;
}
</style>