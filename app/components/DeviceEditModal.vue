<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="edit-modal">
      <h3 class="modal-title">Edit Device</h3>
      <p class="modal-subtitle">Update information for {{ device?.mac || 'selected device' }}</p>

      <div class="form-group">
        <label>Device Name</label>
        <input v-model.trim="form.name" type="text" maxlength="80" />
      </div>

      <div class="form-group">
        <label>Device Type</label>
        <select v-model="form.type">
          <option value="Critical Care">Critical Care</option>
          <option value="Standard">Standard</option>
        </select>
      </div>

      <div class="form-group">
        <label>Assigned Owner</label>
        <select v-model="form.ownerId">
          <option v-for="option in ownerOptions" :key="option.value || 'unassigned'" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="modal-actions">
        <button class="btn-cancel" type="button" @click="emit('close')">Cancel</button>
        <button class="btn-save" type="button" @click="emit('save', { ...form })">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  device: { type: Object, default: null },
  ownerOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'save'])

const form = reactive({
  name: '',
  type: 'Standard',
  ownerId: ''
})

const syncForm = () => {
  form.name = props.device?.name || ''
  form.type = props.device?.type || 'Standard'
  form.ownerId = props.device?.ownerId || ''
}

watch(() => props.device, syncForm, { immediate: true })
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) syncForm()
})
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.42); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 1000; backdrop-filter: blur(10px); }
.edit-modal { width: min(100%, 420px); border-radius: 20px; background: var(--bg-card); border: 1px solid var(--border-color); padding: 22px; box-shadow: 0 28px 70px rgba(15, 23, 42, 0.22); }
.modal-title { margin: 0; font-size: 1.25rem; font-weight: 900; color: var(--text-main); }
.modal-subtitle { margin: 6px 0 18px; color: var(--text-muted); font-size: 0.9rem; }
.form-group { margin-bottom: 14px; display: grid; gap: 6px; }
.form-group label { font-size: 0.78rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; color: #64748b; }
.form-group input, .form-group select { width: 100%; padding: 12px 14px; border-radius: 14px; border: 1px solid rgba(148, 163, 184, 0.2); background: var(--bg-main); color: var(--text-main); box-sizing: border-box; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 22px; }
.btn-cancel { background: var(--bg-main); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 12px; cursor: pointer; color: var(--text-main); font-weight: 800; }
.btn-save { background: linear-gradient(135deg, #0f172a, #2559bd); color: white; border: none; padding: 10px 14px; border-radius: 12px; cursor: pointer; font-weight: 800; }
</style>
