<template>
  <div class="empty-state">
    <div class="empty-icon">
      <span class="material-symbols-outlined" aria-hidden="true">{{ icon }}</span>
    </div>
    <h2>{{ title }}</h2>
    <p v-if="message">{{ message }}</p>
    <slot name="action" />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'info' },
  title: { type: String, required: true },
  message: { type: String, default: '' }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: var(--surface-panel-strong);
  color: rgba(100, 116, 139, 0.85);
  margin-bottom: 18px;
  border: 1px solid var(--surface-border);
}

.empty-icon span {
  font-size: 2.4rem;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
}

h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 900;
  color: var(--text-main);
}

p {
  margin: 8px 0 0;
  max-width: 420px;
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.6;
}
</style>
