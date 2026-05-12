<template>
  <div class="section-page">
    <section class="section-shell">

      <UiPageHeader eyebrow="Administration" title="Staff Team" subtitle="Manage staff members and their roles." back-to="/admin">
        <template #actions>
          <button v-if="canCreateRecords" class="action-button action-button--primary" type="button" @click="openStaffModal()">
            <span class="material-symbols-outlined" aria-hidden="true">add_moderator</span>
            <span>New Staff Member</span>
          </button>
        </template>
      </UiPageHeader>

      <div class="filters-bar">
        <UiSearchInput v-model="search" placeholder="Search by name, role or area..." />
      </div>

      <section class="panel-card">
        <div class="panel-card-header">
          <div>
            <p class="panel-card-eyebrow">Staff</p>
            <h3 class="panel-card-title">Staff Team</h3>
            <p class="panel-card-subtitle">{{ filteredStaff.length }} members</p>
          </div>
        </div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr><th>Name</th><th>Role</th><th>Area</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-if="!filteredStaff.length" class="data-table__empty">
                <td colspan="4">No staff members yet.</td>
              </tr>
              <tr v-for="member in filteredStaff" :key="member.id">
                <td>
                  <div class="cell-avatar">
                    <div class="avatar-circle">{{ member.name.charAt(0) }}</div>
                    <div class="cell-name"><strong>{{ member.name }}</strong><span>{{ member.email }}</span></div>
                  </div>
                </td>
                <td>{{ member.role }}</td>
                <td>{{ member.area }}</td>
                <td style="text-align:center">
                  <button class="entry-link" type="button" @click="openStaffModal(member)">Manage</button>
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

useHead({ title: 'Clinical Sentinel | Staff' })

const {
  search, modal, staffRoles, staffAreas, residents, devices,
  staffForm, residentForm, familyForm, familyUserForm,
  canCreateRecords, modalTitle, filteredStaff,
  openStaffModal, closeModal, syncFamilyResidentLink, syncFamilyUserResidentLink,
  availableDeviceOptions, saveModal
} = useUsersManagement()

const isSaving = ref(false)
const validationMessage = ref('')
const saveAttempt = ref(0)

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const trimValue = (v) => String(v ?? '').trim()
const isEmailValid = (v) => emailPattern.test(trimValue(v))

const isModalValid = computed(() => {
  if (modal.value.type === 'staff') return Boolean(trimValue(staffForm.value.name) && isEmailValid(staffForm.value.email))
  return false
})

const handleSaveModal = async () => {
  if (isSaving.value) return
  saveAttempt.value += 1
  if (!isModalValid.value) { validationMessage.value = 'Please enter a valid name and email.'; return }
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
.cell-avatar { display: inline-flex; align-items: center; gap: 10px; }
.avatar-circle { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #00327d, #0047ab); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 900; flex-shrink: 0; }
.entry-link { border: none; background: transparent; color: #2559bd; font-weight: 800; cursor: pointer; padding: 0; }
.action-button { display: inline-flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 16px; border: 1px solid transparent; font-weight: 900; cursor: pointer; transition: transform 0.2s; }
.action-button:hover { transform: translateY(-1px); }
.action-button--primary { background: linear-gradient(135deg, #00327d 0%, #0047ab 100%); color: #fff; }
.material-symbols-outlined { font-variation-settings: 'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24; display: inline-block; line-height: 1; vertical-align: middle; font-size: 1rem; }
</style>
