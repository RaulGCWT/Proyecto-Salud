<template>
  <div class="page-header-wrap">
    <NuxtLink v-if="backTo" :to="backTo" class="back-link">
      <span class="material-symbols-outlined" aria-hidden="true">arrow_back</span>
      {{ backLabel }}
    </NuxtLink>
    <header class="page-header">
      <div class="page-copy">
        <p class="page-eyebrow">{{ eyebrow }}</p>
        <h1 class="page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="page-actions">
        <slot name="actions" />
      </div>
    </header>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  backTo: { type: String, default: '' },
  backLabel: { type: String, default: 'Admin Dashboard' }
})
</script>

<style scoped>
.page-header-wrap {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(37, 89, 189, 0.2);
  background: rgba(37, 89, 189, 0.06);
  font-size: 0.86rem;
  font-weight: 800;
  color: #2559bd;
  text-decoration: none;
  width: fit-content;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.back-link:hover {
  background: rgba(37, 89, 189, 0.12);
  box-shadow: 0 4px 14px rgba(37, 89, 189, 0.12);
  transform: translateX(-2px);
}

.back-link .material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  font-weight: normal;
  font-style: normal;
  font-size: 1rem;
  text-transform: none;
  white-space: nowrap;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.page-eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 900;
  color: #2559bd;
}

.page-title {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.page-subtitle {
  margin: 8px 0 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
  max-width: 640px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 900px) {
  .page-header {
    align-items: flex-start;
  }

  .page-actions {
    width: 100%;
  }
}
</style>
