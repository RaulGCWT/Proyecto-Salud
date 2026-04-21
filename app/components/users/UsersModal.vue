<template>
  <div v-if="modal.type" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <div class="section-head">
        <h3>{{ modalTitle }}</h3>
        <button class="link-btn" @click="emit('close')">Close</button>
      </div>

      <div v-if="modal.type === 'staff'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input v-model="staffForm.name" class="search" type="text" />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="staffForm.email" class="search" type="email" />
        </label>
        <label class="field">
          <span>Role</span>
          <select v-model="staffForm.role" class="search">
            <option v-for="role in staffRoles" :key="role" :value="role">{{ role }}</option>
          </select>
        </label>
        <label class="field">
          <span>Area</span>
          <select v-model="staffForm.area" class="search">
            <option v-for="area in staffAreas" :key="area" :value="area">{{ area }}</option>
          </select>
        </label>
      </div>

      <div v-else-if="modal.type === 'resident'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input v-model="residentForm.name" class="search" type="text" />
        </label>
        <label class="field">
          <span>Status</span>
          <select v-model="residentForm.status" class="search">
            <option>Active</option>
            <option>Monitoring</option>
            <option>Pending Setup</option>
          </select>
        </label>
        <label class="field">
          <span>Assigned Bed</span>
          <select v-model="residentForm.deviceId" class="search">
            <option value="">Select bed</option>
            <option v-for="device in availableDeviceOptions(residentForm.id)" :key="device.id" :value="device.deviceId">
              {{ device.patientName }} - {{ device.deviceId }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>Notes</span>
          <input v-model="residentForm.notes" class="search" type="text" />
        </label>
      </div>

      <div v-else-if="modal.type === 'family'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input v-model="familyForm.name" class="search" type="text" />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="familyForm.email" class="search" type="email" />
        </label>
        <label class="field">
          <span>Relationship</span>
          <input v-model="familyForm.relationship" class="search" type="text" />
        </label>
        <label class="field">
          <span>State</span>
          <select v-model="familyForm.state" class="search">
            <option>Active</option>
            <option>Pending</option>
          </select>
        </label>
        <label class="field field-full">
          <span>Resident</span>
          <select v-model="familyForm.residentId" class="search" @change="emit('family-resident-change')">
            <option value="">Select resident</option>
            <option v-for="resident in residents" :key="resident.id" :value="resident.id">
              {{ resident.name }}{{ resident.deviceId ? ` - ${resident.deviceId}` : '' }}
            </option>
          </select>
        </label>
      </div>

      <div v-else class="form-grid">
        <label class="field">
          <span>Name</span>
          <input v-model="familyUserForm.name" class="search" type="text" />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="familyUserForm.email" class="search" type="email" />
        </label>
        <label class="field">
          <span>Information</span>
          <input v-model="familyUserForm.relationship" class="search" type="text" />
        </label>
        <label class="field">
          <span>Status</span>
          <select v-model="familyUserForm.state" class="search">
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </label>
        <label class="field field-full">
          <span>Resident</span>
          <select v-model="familyUserForm.residentId" class="search" @change="emit('family-user-resident-change')">
            <option value="">Select resident</option>
            <option v-for="resident in residents" :key="resident.id" :value="resident.id">
              {{ resident.name }}{{ resident.deviceId ? ` - ${resident.deviceId}` : '' }}
            </option>
          </select>
        </label>
        <label class="field field-full">
          <span>Associated device</span>
          <select v-model="familyUserForm.deviceIdOverride" class="search">
            <option value="">Use resident device</option>
            <option v-for="device in devices" :key="device.id" :value="device.deviceId">
              {{ device.patientName }} - {{ device.deviceId }}
            </option>
          </select>
        </label>
      </div>

      <div class="actions">
        <button class="btn btn-muted" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" @click="emit('save')">Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits([
  'close',
  'save',
  'family-resident-change',
  'family-user-resident-change'
])

defineProps({ modal: { type: Object, required: true }, modalTitle: { type: String, required: true }, staffForm: { type: Object, required: true }, residentForm: { type: Object, required: true }, familyForm: { type: Object, required: true }, familyUserForm: { type: Object, required: true }, staffRoles: { type: Array, required: true }, staffAreas: { type: Array, required: true }, residents: { type: Array, required: true }, devices: { type: Array, required: true }, availableDeviceOptions: { type: Function, required: true } })
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, .45); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 1000; }
.modal { width: min(720px, 100%); }
.panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,.08); }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }
.section-head h3 { margin: 0; color: var(--text-main); font-size: 1.05rem; }
.form-grid { display: grid; grid-template-columns: 1fr; gap: 10px; margin: 12px 0; }
.field { display: grid; gap: 6px; color: var(--text-main); font-size: .85rem; }
.field-full { grid-column: auto; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
.search { width: 100%; box-sizing: border-box; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-main); color: var(--text-main); outline: none; }
.btn, .link-btn { border-radius: 6px; font-weight: 600; cursor: pointer; transition: .2s ease; }
.btn { padding: 9px 12px; border: 1px solid var(--border-color); }
.btn-primary { background: #3b82f6; border-color: #3b82f6; color: white; }
.btn-muted { background: var(--bg-main); color: var(--text-main); }
.link-btn { border: none; background: transparent; color: #3b82f6; padding: 0; }
@media (max-width: 820px) { .actions { justify-content: flex-start; } }
</style>
