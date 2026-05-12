<template>
  <div class="section-page">
    <section class="section-shell">

      <UiPageHeader eyebrow="Administration" title="Invitations" subtitle="Manage pending and sent family invitations." back-to="/admin">
        <template #actions>
          <button v-if="canCreateRecords" class="action-button action-button--primary" type="button" @click="openFamilyModal()">
            <span class="material-symbols-outlined" aria-hidden="true">mail</span>
            <span>Send Invite</span>
          </button>
        </template>
      </UiPageHeader>

      <div class="filters-bar">
        <UiSearchInput v-model="search" placeholder="Search by email or resident..." />
      </div>

      <section class="panel-card">
        <div class="panel-card-header">
          <div>
            <p class="panel-card-eyebrow">Invitations</p>
            <h3 class="panel-card-title">Pending Invitations</h3>
            <p class="panel-card-subtitle">{{ filteredInvitations.length }} visible</p>
          </div>
        </div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr><th>Email</th><th>Resident</th><th>Relationship</th><th>State</th><th>Expires</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-if="!filteredInvitations.length" class="data-table__empty">
                <td colspan="6">No invitations yet.</td>
              </tr>
              <tr v-for="invite in filteredInvitations" :key="invite.id">
                <td><strong>{{ invite.email }}</strong></td>
                <td>{{ invite.patientName || '—' }}</td>
                <td>{{ invite.relationship || 'Family' }}</td>
                <td><span :class="['pill', invite.stateClass]">{{ invite.stateLabel }}</span></td>
                <td><span class="entry-meta">{{ formatDate(invite.expiresAt) }}</span></td>
                <td style="text-align:center">
                  <div class="cell-actions">
                    <button v-if="invite.acceptUrl" class="entry-link" type="button" @click="copyInviteLink(invite.acceptUrl)">Copy link</button>
                    <button v-if="invite.state === 'PENDING'" class="entry-link entry-link--danger" type="button" @click="updateInviteState(invite.id, 'CANCELLED')">Cancel</button>
                    <button v-if="invite.state === 'CANCELLED' || invite.state === 'EXPIRED'" class="entry-link" type="button" @click="updateInviteState(invite.id, 'PENDING')">Reopen</button>
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
import { computed, ref, watch } from 'vue'
import { useUsersManagement } from '~/composables/users/useUsersManagement'

useHead({ title: 'Clinical Sentinel | Invitations' })

const {
  search, modal, staffRoles, staffAreas, residents, devices,
  staffForm, residentForm, familyForm, familyUserForm,
  canCreateRecords, modalTitle, filteredInvitations,
  openFamilyModal, closeModal, syncFamilyResidentLink, syncFamilyUserResidentLink,
  availableDeviceOptions, saveModal, formatDate, copyInviteLink, updateInviteState
} = useUsersManagement()

const isSaving = ref(false)
const validationMessage = ref('')
const saveAttempt = ref(0)

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const trimValue = (v) => String(v ?? '').trim()
const isEmailValid = (v) => emailPattern.test(trimValue(v))

const isModalValid = computed(() => {
  if (modal.value.type === 'family') return Boolean(trimValue(familyForm.value.name) && isEmailValid(familyForm.value.email) && trimValue(familyForm.value.residentId))
  return false
})

const handleSaveModal = async () => {
  if (isSaving.value) return
  saveAttempt.value += 1
  if (!isModalValid.value) { validationMessage.value = 'Please enter name, email and resident.'; return }
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
.cell-actions { display: inline-flex; gap: 12px; justify-content: center; }
.entry-link { border: none; background: transparent; color: #2559bd; font-weight: 800; cursor: pointer; padding: 0; }
.entry-link--danger { color: #ef4444; }
.entry-meta { color: var(--text-muted); font-size: 0.84rem; }
.pill { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 900; text-transform: uppercase; }
.action-button { display: inline-flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 16px; border: 1px solid transparent; font-weight: 900; cursor: pointer; transition: transform 0.2s; }
.action-button:hover { transform: translateY(-1px); }
.action-button--primary { background: linear-gradient(135deg, #00327d 0%, #0047ab 100%); color: #fff; }
.material-symbols-outlined { font-variation-settings: 'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24; display: inline-block; line-height: 1; vertical-align: middle; font-size: 1rem; }
</style>
