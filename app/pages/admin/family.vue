<template>
  <div class="section-page">
    <section class="section-shell">

      <UiPageHeader eyebrow="Administration" title="Family Access" subtitle="Manage family users and their access to resident data." back-to="/admin">
        <template #actions>
          <button v-if="canCreateRecords" class="action-button action-button--primary" type="button" @click="openFamilyModal()">
            <span class="material-symbols-outlined" aria-hidden="true">mail</span>
            <span>Invite Family</span>
          </button>
        </template>
      </UiPageHeader>

      <div class="filters-bar">
        <UiSearchInput v-model="search" placeholder="Search by name, email or resident..." />
      </div>

      <section class="panel-card">
        <div class="panel-card-header">
          <div>
            <p class="panel-card-eyebrow">Family</p>
            <h3 class="panel-card-title">Family Access</h3>
            <p class="panel-card-subtitle">{{ filteredFamilies.length }} users</p>
          </div>
        </div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr><th>Name</th><th>Family of</th><th>Relationship</th><th>State</th><th>Device</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-if="!filteredFamilies.length" class="data-table__empty">
                <td colspan="6">No family users yet.</td>
              </tr>
              <tr v-for="relative in filteredFamilies" :key="relative.id">
                <td>
                  <div class="cell-name"><strong>{{ relative.name }}</strong><span>{{ relative.email }}</span></div>
                </td>
                <td>{{ relative.patientName || '—' }}</td>
                <td>{{ relative.relationship || '—' }}</td>
                <td><span :class="['pill', relative.state === 'Active' ? 'pill--success' : 'pill--warning']">{{ relative.state }}</span></td>
                <td>
                  <code v-if="relative.deviceId" class="entry-chip">{{ relative.deviceId }}</code>
                  <span v-else class="entry-meta">—</span>
                </td>
                <td style="text-align:center">
                  <div class="cell-actions">
                    <button class="entry-link" type="button" @click="openFamilyUserModal(relative)">Edit</button>
                    <button class="entry-link" type="button" @click="toggleFamilyState(relative.id)">{{ relative.state === 'Active' ? 'Deactivate' : 'Activate' }}</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <UsersModal
        :modal="modal" :modal-title="modalTitle"
        :staff-form="staffForm" :resident-form="residentForm"
        :family-form="familyForm" :family-user-form="familyUserForm"
        :is-saving="isSaving" :can-save="isModalValid"
        :validation-message="validationMessage" :save-attempt="saveAttempt"
        :staff-roles="staffRoles" :staff-areas="staffAreas"
        :residents="residents" :devices="devices"
        :available-device-options="availableDeviceOptions"
        @close="closeModal" @save="handleSaveModal"
        @family-resident-change="syncFamilyResidentLink"
        @family-user-resident-change="syncFamilyUserResidentLink"
      />

    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useUsersManagement } from '~/composables/users/useUsersManagement'

useHead({ title: 'Clinical Sentinel | Family' })

const {
  search, modal, staffRoles, staffAreas, residents, devices,
  staffForm, residentForm, familyForm, familyUserForm,
  canCreateRecords, modalTitle, filteredFamilies,
  openFamilyModal, openFamilyUserModal, closeModal,
  syncFamilyResidentLink, syncFamilyUserResidentLink,
  availableDeviceOptions, saveModal, toggleFamilyState
} = useUsersManagement()

const isSaving = ref(false)
const validationMessage = ref('')
const saveAttempt = ref(0)

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const trimValue = (v) => String(v ?? '').trim()
const isEmailValid = (v) => emailPattern.test(trimValue(v))

const isModalValid = computed(() => {
  if (modal.value.type === 'family') return Boolean(trimValue(familyForm.value.name) && isEmailValid(familyForm.value.email) && trimValue(familyForm.value.residentId))
  if (modal.value.type === 'family-user') return Boolean(trimValue(familyUserForm.value.name) && isEmailValid(familyUserForm.value.email) && trimValue(familyUserForm.value.residentId))
  return false
})

const handleSaveModal = async () => {
  if (isSaving.value) return
  saveAttempt.value += 1
  if (!isModalValid.value) { validationMessage.value = 'Please complete all required fields.'; return }
  validationMessage.value = ''
  isSaving.value = true
  try { await saveModal() } finally { isSaving.value = false }
}

watch(() => modal.value.type, (t) => { if (!t) { validationMessage.value = ''; saveAttempt.value = 0 } })
watch(isModalValid, (v) => { if (v) validationMessage.value = '' })
</script>

<style scoped>
.section-page { display: grid; }
.section-shell { display: flex; flex-direction: column; gap: 22px; max-width: 1440px; margin: 0 auto; width: 100%; }
.cell-name { display: flex; flex-direction: column; gap: 3px; }
.cell-name strong { font-size: 0.96rem; font-weight: 800; }
.cell-name span { font-size: 0.8rem; color: var(--text-muted); }
.cell-actions { display: inline-flex; gap: 12px; justify-content: center; }
.entry-link { border: none; background: transparent; color: #2559bd; font-weight: 800; cursor: pointer; padding: 0; }
.entry-chip { display: inline-flex; align-items: center; padding: 5px 10px; border-radius: 999px; background: rgba(37,99,235,0.16); color: #93c5fd; border: 1px solid rgba(59,130,246,0.24); font-size: 0.76rem; font-weight: 800; }
.entry-meta { color: var(--text-muted); font-size: 0.84rem; }
.pill { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 900; text-transform: uppercase; }
.pill--success { background: rgba(16,185,129,0.18); color: #6ee7b7; }
.pill--warning { background: rgba(249,115,22,0.18); color: #fdba74; }
.action-button { display: inline-flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 16px; border: 1px solid transparent; font-weight: 900; cursor: pointer; transition: transform 0.2s; }
.action-button:hover { transform: translateY(-1px); }
.action-button--primary { background: linear-gradient(135deg, #00327d 0%, #0047ab 100%); color: #fff; }
.material-symbols-outlined { font-variation-settings: 'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24; display: inline-block; line-height: 1; vertical-align: middle; font-size: 1rem; }
</style>
