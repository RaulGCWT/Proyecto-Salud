<template>
  <div class="filter-wrap" @click.stop>
    <button
      class="filter-button"
      type="button"
      :aria-expanded="isOpen ? 'true' : 'false'"
      @click="isOpen = !isOpen"
    >
      <span class="filter-button__label">{{ label }}</span>
      <span class="filter-button__value">{{ selectedLabel }}</span>
      <span class="filter-button__icon" aria-hidden="true">▾</span>
    </button>

    <div v-if="isOpen" class="filter-menu">
      <button
        v-for="option in options"
        :key="option.value"
        class="filter-menu__item"
        :class="{ 'filter-menu__item--active': modelValue === option.value }"
        type="button"
        @click="select(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: String, default: 'all' },
  options: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const selectedLabel = computed(() => {
  return props.options.find(o => o.value === props.modelValue)?.label || props.options[0]?.label || ''
})

function select(value) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function closeOnOutsideClick(event) {
  if (!event.target.closest('.filter-wrap')) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', closeOnOutsideClick))
onBeforeUnmount(() => document.removeEventListener('click', closeOnOutsideClick))
</script>

<style scoped>
.filter-wrap {
  position: relative;
  min-width: 150px;
}

.filter-button {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 13px 16px;
  border-radius: 18px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: var(--text-main);
  cursor: pointer;
  box-sizing: border-box;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.filter-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04);
}

.filter-button__label {
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  white-space: nowrap;
}

.filter-button__value {
  flex: 1;
  text-align: left;
  font-size: 0.9rem;
  font-weight: 900;
  color: var(--text-main);
  white-space: nowrap;
}

.filter-button__icon {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1;
}

.filter-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  z-index: 25;
  width: 100%;
  padding: 8px;
  border-radius: 18px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 22px 44px var(--surface-shadow);
}

.filter-menu__item {
  width: 100%;
  padding: 11px 12px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--text-main);
  font-size: 0.82rem;
  font-weight: 800;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s ease, color 0.2s ease;
}

.filter-menu__item:hover {
  background: rgba(37, 89, 189, 0.08);
  color: #2559bd;
}

.filter-menu__item--active {
  background: rgba(37, 89, 189, 0.1);
  color: #2559bd;
}
</style>
