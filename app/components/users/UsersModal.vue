<template>
  <div v-if="modal.type" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">User form</p>
          <h3>{{ modalTitle }}</h3>
          <p class="section-subtitle">
            Check the main details and review the resident or device relationship before saving.
          </p>
        </div>
        <button class="close-button" type="button" @click="emit('close')">
          <span class="material-symbols-outlined" aria-hidden="true">close</span>
        </button>
      </div>

      <div v-if="modal.type === 'staff'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input
            v-model="staffForm.name"
            class="search"
            :class="{ 'search--invalid': isStaffNameInvalid }"
            ref="staffNameInput"
            type="text"
            autocomplete="name"
          />
          <small v-if="isStaffNameInvalid" class="field-error">{{ getRequiredMessage('Name') }}</small>
        </label>
        <label class="field">
          <span>Email</span>
          <input
            v-model="staffForm.email"
            class="search"
            :class="{ 'search--invalid': isStaffEmailInvalid }"
            ref="staffEmailInput"
            type="email"
            autocomplete="email"
          />
          <small v-if="isStaffEmailInvalid" class="field-error">{{ getEmailMessage(staffForm.email) }}</small>
        </label>
        <label class="field">
          <span>Role</span>
          <div class="select-shell">
            <select v-model="staffForm.role" class="search search--select">
              <option v-for="role in staffRoles" :key="role" :value="role">{{ role }}</option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
        <label class="field">
          <span>Area</span>
          <div class="select-shell">
            <select v-model="staffForm.area" class="search search--select">
              <option v-for="area in staffAreas" :key="area" :value="area">{{ area }}</option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
      </div>

      <div v-else-if="modal.type === 'resident'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input
            v-model="residentForm.name"
            class="search"
            :class="{ 'search--invalid': isResidentNameInvalid }"
            ref="residentNameInput"
            type="text"
            autocomplete="name"
          />
          <small v-if="isResidentNameInvalid" class="field-error">{{ getRequiredMessage('Name') }}</small>
        </label>
        <label class="field">
          <span>Status</span>
          <div class="select-shell">
            <select v-model="residentForm.status" class="search search--select">
              <option>Active</option>
              <option>Monitoring</option>
              <option>Pending Setup</option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
        <label class="field">
          <span>Assigned Bed</span>
          <div class="select-shell">
            <select v-model="residentForm.deviceId" class="search search--select">
              <option value="">Select bed</option>
              <option v-for="device in availableDeviceOptions(residentForm.id)" :key="device.id" :value="device.deviceId">
                {{ device.patientName }} - {{ device.deviceId }}
              </option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
        <label class="field">
          <span>Notes</span>
          <input v-model="residentForm.notes" class="search" type="text" autocomplete="off" />
        </label>
      </div>

      <div v-else-if="modal.type === 'family'" class="form-grid">
        <label class="field">
          <span>Name</span>
          <input
            v-model="familyForm.name"
            class="search"
            :class="{ 'search--invalid': isFamilyNameInvalid }"
            ref="familyNameInput"
            type="text"
            autocomplete="name"
          />
          <small v-if="isFamilyNameInvalid" class="field-error">{{ getRequiredMessage('Name') }}</small>
        </label>
        <label class="field">
          <span>Email</span>
          <input
            v-model="familyForm.email"
            class="search"
            :class="{ 'search--invalid': isFamilyEmailInvalid }"
            ref="familyEmailInput"
            type="email"
            autocomplete="email"
          />
          <small v-if="isFamilyEmailInvalid" class="field-error">{{ getEmailMessage(familyForm.email) }}</small>
        </label>
        <label class="field">
          <span>Relationship</span>
          <input v-model="familyForm.relationship" class="search" type="text" autocomplete="off" />
        </label>
        <label class="field">
          <span>State</span>
          <div class="select-shell">
            <select v-model="familyForm.state" class="search search--select">
              <option>Active</option>
              <option>Pending</option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
        <label class="field field-full field-spaced">
          <span>Resident</span>
          <div class="select-shell" :class="{ 'select-shell--invalid': isFamilyResidentInvalid }">
            <select
              v-model="familyForm.residentId"
              class="search search--select"
              ref="familyResidentSelect"
              @change="emit('family-resident-change')"
            >
              <option value="">Select resident</option>
              <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}{{ resident.deviceId ? ` - ${resident.deviceId}` : '' }}
              </option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
          <small v-if="isFamilyResidentInvalid" class="field-error">Select a resident.</small>
        </label>
      </div>

      <div v-else class="form-grid">
        <label class="field">
          <span>Name</span>
          <input
            v-model="familyUserForm.name"
            class="search"
            :class="{ 'search--invalid': isFamilyUserNameInvalid }"
            ref="familyUserNameInput"
            type="text"
            autocomplete="name"
          />
          <small v-if="isFamilyUserNameInvalid" class="field-error">{{ getRequiredMessage('Name') }}</small>
        </label>
        <label class="field">
          <span>Email</span>
          <input
            v-model="familyUserForm.email"
            class="search"
            :class="{ 'search--invalid': isFamilyUserEmailInvalid }"
            ref="familyUserEmailInput"
            type="email"
            autocomplete="email"
          />
          <small v-if="isFamilyUserEmailInvalid" class="field-error">{{ getEmailMessage(familyUserForm.email) }}</small>
        </label>
        <label class="field">
          <span>Information</span>
          <input v-model="familyUserForm.relationship" class="search" type="text" autocomplete="off" />
        </label>
        <label class="field">
          <span>Status</span>
          <div class="select-shell">
            <select v-model="familyUserForm.state" class="search search--select">
              <option>Active</option>
              <option>Inactive</option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
        <label class="field field-full field-spaced">
          <span>Resident</span>
          <div class="select-shell" :class="{ 'select-shell--invalid': isFamilyUserResidentInvalid }">
            <select
              v-model="familyUserForm.residentId"
              class="search search--select"
              ref="familyUserResidentSelect"
              @change="emit('family-user-resident-change')"
            >
              <option value="">Select resident</option>
              <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}{{ resident.deviceId ? ` - ${resident.deviceId}` : '' }}
              </option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
          <small v-if="isFamilyUserResidentInvalid" class="field-error">Select a resident.</small>
        </label>
        <label class="field field-full field-spaced">
          <span>Associated device</span>
          <div class="select-shell">
            <select v-model="familyUserForm.deviceIdOverride" class="search search--select">
              <option value="">Use resident device</option>
              <option v-for="device in devices" :key="device.id" :value="device.deviceId">
                {{ device.patientName }} - {{ device.deviceId }}
              </option>
            </select>
            <span class="material-symbols-outlined select-shell__icon" aria-hidden="true">expand_more</span>
          </div>
        </label>
      </div>

      <div class="actions">
        <p v-if="validationMessage" class="validation-message" role="alert">
          {{ validationMessage }}
        </p>
        <button class="btn btn-muted" type="button" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" :class="{ 'btn--inactive': !canSave && !isSaving }" type="button" :disabled="isSaving" @click="emit('save')">
          <span v-if="isSaving" class="button-spinner" aria-hidden="true"></span>
          <span>{{ isSaving ? 'Saving...' : 'Save' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'

const emit = defineEmits([
  'close',
  'save',
  'family-resident-change',
  'family-user-resident-change'
])

const props = defineProps({
  modal: { type: Object, required: true },
  modalTitle: { type: String, required: true },
  staffForm: { type: Object, required: true },
  residentForm: { type: Object, required: true },
  familyForm: { type: Object, required: true },
  familyUserForm: { type: Object, required: true },
  isSaving: { type: Boolean, default: false },
  canSave: { type: Boolean, default: true },
  validationMessage: { type: String, default: '' },
  saveAttempt: { type: Number, default: 0 },
  staffRoles: { type: Array, required: true },
  staffAreas: { type: Array, required: true },
  residents: { type: Array, required: true },
  devices: { type: Array, required: true },
  availableDeviceOptions: { type: Function, required: true }
})

const staffNameInput = ref(null)
const staffEmailInput = ref(null)
const residentNameInput = ref(null)
const familyNameInput = ref(null)
const familyEmailInput = ref(null)
const familyResidentSelect = ref(null)
const familyUserNameInput = ref(null)
const familyUserEmailInput = ref(null)
const familyUserResidentSelect = ref(null)

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const trimValue = (value) => String(value ?? '').trim()

const isEmailValid = (value) => emailPattern.test(trimValue(value))

const isStaffNameInvalid = computed(() => !trimValue(props.staffForm.name))
const isStaffEmailInvalid = computed(() => !trimValue(props.staffForm.email) || !isEmailValid(props.staffForm.email))
const isResidentNameInvalid = computed(() => !trimValue(props.residentForm.name))

const isFamilyNameInvalid = computed(() => !trimValue(props.familyForm.name))
const isFamilyEmailInvalid = computed(() => !trimValue(props.familyForm.email) || !isEmailValid(props.familyForm.email))
const isFamilyResidentInvalid = computed(() => !trimValue(props.familyForm.residentId))

const isFamilyUserNameInvalid = computed(() => !trimValue(props.familyUserForm.name))
const isFamilyUserEmailInvalid = computed(() => !trimValue(props.familyUserForm.email) || !isEmailValid(props.familyUserForm.email))
const isFamilyUserResidentInvalid = computed(() => !trimValue(props.familyUserForm.residentId))

const getRequiredMessage = (label) => `${label} is required.`

const getEmailMessage = (value) => {
  if (!trimValue(value)) {
    return 'Email is required.'
  }

  return 'Enter a valid email address.'
}

const focusFirstInvalidField = async () => {
  await nextTick()

  if (props.modal.type === 'staff') {
    if (isStaffNameInvalid.value) {
      staffNameInput.value?.focus?.()
      return
    }

    if (isStaffEmailInvalid.value) {
      staffEmailInput.value?.focus?.()
      return
    }
  }

  if (props.modal.type === 'resident') {
    if (isResidentNameInvalid.value) {
      residentNameInput.value?.focus?.()
    }
    return
  }

  if (props.modal.type === 'family') {
    if (isFamilyNameInvalid.value) {
      familyNameInput.value?.focus?.()
      return
    }

    if (isFamilyEmailInvalid.value) {
      familyEmailInput.value?.focus?.()
      return
    }

    if (isFamilyResidentInvalid.value) {
      familyResidentSelect.value?.focus?.()
    }
    return
  }

  if (props.modal.type === 'family-user') {
    if (isFamilyUserNameInvalid.value) {
      familyUserNameInput.value?.focus?.()
      return
    }

    if (isFamilyUserEmailInvalid.value) {
      familyUserEmailInput.value?.focus?.()
      return
    }

    if (isFamilyUserResidentInvalid.value) {
      familyUserResidentSelect.value?.focus?.()
    }
  }
}

watch(
  () => props.saveAttempt,
  async () => {
    if (!props.saveAttempt || props.canSave) {
      return
    }

    await focusFirstInvalidField()
  }
)
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
  backdrop-filter: blur(12px);
}

.modal {
  width: min(760px, 100%);
}

.panel {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 28px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.18);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 22px 24px 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(248, 250, 252, 0.95));
}

.section-head h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.5rem;
  font-weight: 900;
  letter-spacing: -0.04em;
}

.section-eyebrow {
  margin: 0 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 900;
  color: #2559bd;
}

.section-subtitle {
  margin: 8px 0 0;
  max-width: 540px;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

.close-button {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(248, 250, 252, 0.95);
  color: #475569;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, color 0.2s ease;
}

.close-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(37, 89, 189, 0.08);
  color: #2559bd;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 14px;
  padding: 24px;
}

.field {
  display: grid;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.82rem;
}

.field > small {
  margin-top: -2px;
}

.field-full {
  grid-column: auto;
}

.field-spaced {
  margin-top: 4px;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
  padding: 0 24px 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
  padding-top: 18px;
  background: rgba(248, 250, 252, 0.7);
}

.validation-message {
  flex: 1 1 100%;
  margin: 0;
  color: #b91c1c;
  font-size: 0.82rem;
  font-weight: 700;
}

.field-error {
  color: #b91c1c;
  font-size: 0.74rem;
  font-weight: 700;
  line-height: 1.35;
}

.search {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  background: linear-gradient(180deg, #fbfcfe 0%, #f8fafc 100%);
  color: var(--text-main);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.search:focus {
  border-color: rgba(37, 89, 189, 0.34);
  box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.08);
  background: #ffffff;
}

.search:hover {
  border-color: rgba(37, 89, 189, 0.24);
}

.search--invalid {
  border-color: rgba(239, 68, 68, 0.28);
  background: linear-gradient(180deg, #fffafa 0%, #fff7f7 100%);
}

.search--invalid:focus {
  border-color: rgba(239, 68, 68, 0.42);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.08);
}

.search--invalid:hover {
  border-color: rgba(239, 68, 68, 0.34);
}

.search--select {
  padding-right: 44px;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.select-shell {
  position: relative;
}

.select-shell--invalid .search {
  border-color: rgba(239, 68, 68, 0.28);
  background: linear-gradient(180deg, #fffafa 0%, #fff7f7 100%);
}

.select-shell--invalid .search:focus {
  border-color: rgba(239, 68, 68, 0.42);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.08);
}

.select-shell__icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #637188;
  font-size: 1.05rem;
  pointer-events: none;
}

.btn,
.link-btn {
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.2s ease;
}

.btn {
  padding: 11px 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.btn:disabled {
  opacity: 0.72;
  cursor: wait;
  transform: none;
}

.btn--inactive {
  opacity: 0.9;
}

.btn-primary {
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 14px 30px rgba(37, 89, 189, 0.18);
}

.btn-muted {
  background: var(--bg-main);
  color: var(--text-main);
}

.link-btn {
  border: none;
  background: transparent;
  color: #3b82f6;
  padding: 0;
}

.button-spinner {
  width: 14px;
  height: 14px;
  border-radius: 9999px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: #ffffff;
  display: inline-block;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 820px) {
  .section-head {
    padding: 20px 18px 16px;
  }

  .section-head h3 {
    font-size: 1.28rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
    padding: 18px;
  }

  .search--select {
    padding-right: 40px;
  }

  .actions {
    justify-content: flex-start;
    padding: 18px;
    padding-top: 16px;
  }

  .section-subtitle {
    max-width: none;
    font-size: 0.86rem;
  }

  .validation-message {
    flex-basis: 100%;
  }
}
</style>
