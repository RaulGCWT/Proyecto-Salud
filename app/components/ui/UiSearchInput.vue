<template>
  <div class="search-wrap">
    <span class="material-symbols-outlined search-icon" aria-hidden="true">search</span>
    <input
      :value="modelValue"
      class="search-input"
      type="text"
      :placeholder="placeholder"
      autocomplete="off"
      @input="emit('update:modelValue', $event.target.value.trim())"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search...' }
})

const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
.search-wrap {
  position: relative;
  flex: 1 1 320px;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(100, 116, 139, 0.7);
  font-size: 1.1rem;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}

.search-input {
  width: 100%;
  padding: 13px 16px 13px 46px;
  border-radius: 18px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: var(--text-main);
  font-weight: 700;
  box-sizing: border-box;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-muted);
}
</style>
