<template>
  <Transition name="toast">
    <div v-if="modelValue" class="toast-notification" @click="$emit('update:modelValue', null)">
      <div class="toast-icon">⚠️</div>
      <div class="toast-body">
        <div class="toast-title">ALERTA CRÍTICA</div>
        <div class="toast-desc">{{ modelValue.sensor }}: {{ modelValue.message }}</div>
      </div>
      <button class="toast-close">✕</button>
    </div>
  </Transition>
</template>

<script setup>
defineProps(['modelValue'])
defineEmits(['update:modelValue'])
</script>

<style scoped>
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #0f172a;
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 9999;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  border-left: 6px solid #ef4444;
  cursor: pointer;
  min-width: 300px;
  font-family: 'Inter', sans-serif;
}

.toast-title {
  font-weight: 800;
  font-size: 0.75rem;
  color: #ef4444;
  text-transform: uppercase;
}

.toast-desc { font-size: 0.9rem; color: #e2e8f0; }
.toast-close { background: none; border: none; color: #94a3b8; margin-left: auto; cursor: pointer; }

/* Animación */
.toast-enter-active, .toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from { transform: translateX(100%) scale(0.5); opacity: 0; }
.toast-leave-to { transform: translateX(100%); opacity: 0; }
</style>