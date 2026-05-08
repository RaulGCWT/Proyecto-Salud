<template>
  <article class="summary-card">
    <div class="summary-top">
      <span v-if="icon" :class="['summary-icon', `summary-icon--${tone}`]" aria-hidden="true">
        <span class="material-symbols-outlined">{{ icon }}</span>
      </span>
      <span class="summary-label">{{ label }}</span>
    </div>
    <strong class="summary-value">{{ value }}</strong>
    <p v-if="note" class="summary-note">{{ note }}</p>
  </article>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  label: { type: String, required: true },
  value: { type: String, required: true },
  note: { type: String, default: '' },
  tone: { type: String, default: 'blue' }
})
</script>

<style scoped>
.summary-card {
  padding: 22px;
  border-radius: 24px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 14px 34px var(--surface-shadow);
}

.summary-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.summary-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.summary-icon span { font-size: 1.2rem; }

.summary-icon--blue  { color: #2559bd; background: rgba(37, 89, 189, 0.1); }
.summary-icon--red   { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.summary-icon--teal  { color: #047857; background: rgba(16, 185, 129, 0.1); }
.summary-icon--amber { color: #b45309; background: rgba(245, 158, 11, 0.12); }

.summary-label {
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.summary-value {
  display: block;
  margin: 0;
  font-size: clamp(1.9rem, 3vw, 2.7rem);
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
  line-height: 1;
}

.summary-note {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.5;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}
</style>
