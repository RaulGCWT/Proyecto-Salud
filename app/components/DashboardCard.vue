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
const props = defineProps({ title: String, mainText: String, description: String, isAlert: Boolean, type: String });

const colorClass = computed(() => {
  if (props.type === 'hr') return 'heart-color';
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
  transition: all 0.4s ease; /* Transición suave para el cambio de color */
  border-left: 5px solid #cbd5e1; 
}

/* Estilo especial cuando la cama está vacía */
.is-empty {
  background-color: #f1f5f9 !important; /* Gris muy claro */
  border-left-color: #94a3b8 !important; /* Borde gris oscuro */
  opacity: 0.8;
}

.is-empty .presence-color {
  color: #64748b !important; /* Texto en gris en lugar de verde */
}

/* Colores originales */
.type-hr { border-left-color: #ef4444; }
.type-hrv { border-left-color: #06b6d4; }
.type-resp { border-left-color: #8b5cf6; }
.type-presence { border-left-color: #10b981; }

.card-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.card-value { font-size: 2rem; font-weight: 800; margin: 8px 0; }
.heart-color { color: #ef4444; }
.resp-color { color: #8b5cf6; }
.presence-color { color: #10b981; }

.card-indicator { font-size: 0.85rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; display: inline-block; }
.status-ok { background: #dcfce7; color: #166534; }
.status-error { background: #fee2e2; color: #991b1b; }
</style>