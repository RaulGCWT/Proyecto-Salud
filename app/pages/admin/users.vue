<template>
  <div class="users-page">
    <section class="users-shell">
      <header class="page-header">
        <div class="page-copy">
          <p class="page-eyebrow">Enterprise management</p>
          <h1 class="page-title">User Management</h1>
          <p class="page-subtitle">
            Manage staff, residents, family access, pending invitations and available beds from a single control panel.
          </p>
        </div>

        <div class="page-actions">
          <button v-if="canCreateRecords" class="action-button action-button--soft" type="button" @click="openFamilyModal()">
            <span class="material-symbols-outlined" aria-hidden="true">mail</span>
            <span>Invite Family</span>
          </button>
          <button v-if="canCreateRecords" class="action-button action-button--secondary" type="button" @click="openResidentModal()">
            <span class="material-symbols-outlined" aria-hidden="true">person</span>
            <span>Create Resident</span>
          </button>
          <button v-if="canCreateRecords" class="action-button action-button--primary" type="button" @click="openStaffModal()">
            <span class="material-symbols-outlined" aria-hidden="true">add_moderator</span>
            <span>Create Staff</span>
          </button>
        </div>
      </header>

      <div v-if="toastMessage" class="toast" role="status" aria-live="polite">
        <span class="material-symbols-outlined" aria-hidden="true">check_circle</span>
        <span>{{ toastMessage }}</span>
      </div>

      <section class="summary-grid">
        <article v-for="item in summaryCards" :key="item.label" class="summary-card">
          <div class="summary-card__top">
            <span class="summary-label">{{ item.label }}</span>
          </div>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-meta">{{ item.meta }}</p>
        </article>
      </section>

      <section class="toolbar-panel">
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab', { active: activeTab === tab.id }]"
            type="button"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <label class="search-field">
          <span class="material-symbols-outlined search-field__icon" aria-hidden="true">search</span>
          <input
            v-model="search"
            class="search-input"
            type="text"
            placeholder="Search by user, resident, family or device..."
            autocomplete="off"
          />
        </label>
      </section>

      <section class="content-grid">
        <article v-if="showSection('staff')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Staff</p>
              <h2 class="section-title">Staff Team</h2>
            </div>
            <button v-if="canCreateRecords" class="section-action" type="button" @click="openStaffModal()">
              New user
            </button>
          </div>

          <div class="table-wrapper">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Area</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredStaff.length" class="admin-table__empty">
                  <td colspan="4">No staff members yet.</td>
                </tr>
                <tr v-for="member in filteredStaff" :key="member.id">
                  <td>
                    <div class="cell-avatar">
                      <div class="avatar-circle">{{ member.name.charAt(0) }}</div>
                      <div class="cell-name">
                        <strong>{{ member.name }}</strong>
                        <span>{{ member.email }}</span>
                      </div>
                    </div>
                  </td>
                  <td>{{ member.role }}</td>
                  <td>{{ member.area }}</td>
                  <td>
                    <button class="entry-link" type="button" @click="openStaffModal(member)">Manage</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article v-if="showSection('residents')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Residents</p>
              <h2 class="section-title">Resident Directory</h2>
            </div>
            <button v-if="canCreateRecords" class="section-action" type="button" @click="openResidentModal()">
              New resident
            </button>
          </div>

          <div class="table-wrapper">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Assigned Bed</th>
                  <th>Family</th>
                  <th>Notes</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredResidents.length" class="admin-table__empty">
                  <td colspan="6">No residents yet.</td>
                </tr>
                <tr v-for="resident in filteredResidents" :key="resident.id">
                  <td><strong>{{ resident.name }}</strong></td>
                  <td>{{ resident.status || '—' }}</td>
                  <td>
                    <code v-if="resident.deviceId" class="entry-chip">{{ resident.deviceId }}</code>
                    <span v-else class="entry-meta">Unassigned</span>
                  </td>
                  <td>{{ familyCountForResident(resident.name) }}</td>
                  <td><span class="entry-meta">{{ resident.notes || '—' }}</span></td>
                  <td>
                    <div class="cell-actions">
                      <button class="entry-link" type="button" @click="openResidentModal(resident)">Edit</button>
                      <button v-if="canCreateRecords" class="entry-link" type="button" @click="openFamilyModalForResident(resident)">Invite Family</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article v-if="showSection('family')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Family</p>
              <h2 class="section-title">Family Access</h2>
            </div>
            <button v-if="canCreateRecords" class="section-action" type="button" @click="openFamilyModal()">
              Send invite
            </button>
          </div>

          <div class="table-wrapper">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Family of</th>
                  <th>Relationship</th>
                  <th>State</th>
                  <th>Device</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredFamilies.length" class="admin-table__empty">
                  <td colspan="6">No family users yet.</td>
                </tr>
                <tr v-for="relative in filteredFamilies" :key="relative.id">
                  <td>
                    <div class="cell-name">
                      <strong>{{ relative.name }}</strong>
                      <span>{{ relative.email }}</span>
                    </div>
                  </td>
                  <td>{{ relative.patientName || '—' }}</td>
                  <td>{{ relative.relationship || '—' }}</td>
                  <td>
                    <span :class="['pill', relative.state === 'Active' ? 'pill--success' : 'pill--warning']">
                      {{ relative.state }}
                    </span>
                  </td>
                  <td>
                    <code v-if="relative.deviceId" class="entry-chip">{{ relative.deviceId }}</code>
                    <span v-else class="entry-meta">—</span>
                  </td>
                  <td>
                    <div class="cell-actions">
                      <button class="entry-link" type="button" @click="openFamilyUserModal(relative)">Edit</button>
                      <button class="entry-link" type="button" @click="toggleFamilyState(relative.id)">
                        {{ relative.state === 'Active' ? 'Deactivate' : 'Activate' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article v-if="showSection('invitations')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Invitations</p>
              <h2 class="section-title">Pending Invitations</h2>
            </div>
            <span class="section-count">{{ filteredInvitations.length }} visible</span>
          </div>

          <div class="table-wrapper">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Resident</th>
                  <th>Relationship</th>
                  <th>State</th>
                  <th>Expires</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredInvitations.length" class="admin-table__empty">
                  <td colspan="6">No invitations match the current filter.</td>
                </tr>
                <tr v-for="invite in filteredInvitations" :key="invite.id">
                  <td><strong>{{ invite.email }}</strong></td>
                  <td>{{ invite.patientName || '—' }}</td>
                  <td>{{ invite.relationship || 'Family' }}</td>
                  <td><span :class="['pill', invite.stateClass]">{{ invite.stateLabel }}</span></td>
                  <td><span class="entry-meta">{{ formatDate(invite.expiresAt) }}</span></td>
                  <td>
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
        </article>

        <article v-if="showSection('devices')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Beds</p>
              <h2 class="section-title">Available Beds</h2>
            </div>
          </div>

          <div class="table-wrapper">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Device</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="resourcesLoading" class="admin-table__empty">
                  <td colspan="3">Loading devices...</td>
                </tr>
                <tr v-else-if="!filteredDevices.length" class="admin-table__empty">
                  <td colspan="3">No devices found in the database.</td>
                </tr>
                <tr v-else v-for="device in filteredDevices" :key="device.id">
                  <td><strong>{{ device.patientName }}</strong></td>
                  <td><code class="entry-chip">{{ device.deviceId }}</code></td>
                  <td>
                    <span :class="['pill', isAssignedDevice(device.deviceId) ? 'pill--warning' : 'pill--success']">
                      {{ isAssignedDevice(device.deviceId) ? 'Assigned' : 'Available' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <UsersModal
        :modal="modal"
        :modal-title="modalTitle"
        :staff-form="staffForm"
        :resident-form="residentForm"
        :family-form="familyForm"
        :family-user-form="familyUserForm"
        :is-saving="isSaving"
        :can-save="isModalValid"
        :validation-message="validationMessage"
        :save-attempt="saveAttempt"
        :staff-roles="staffRoles"
        :staff-areas="staffAreas"
        :residents="residents"
        :devices="devices"
        :available-device-options="availableDeviceOptions"
        @close="closeModal"
        @save="handleSaveModal"
        @family-resident-change="syncFamilyResidentLink"
        @family-user-resident-change="syncFamilyUserResidentLink"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useUsersManagement } from '~/composables/users/useUsersManagement'

const {
  search,
  activeTab,
  modal,
  tabs,
  staffRoles,
  staffAreas,
  residents,
  devices,
  resourcesLoading,
  staffForm,
  residentForm,
  familyForm,
  familyUserForm,
  canCreateRecords,
  summaryCards,
  modalTitle,
  filteredStaff,
  filteredResidents,
  filteredFamilies,
  filteredInvitations,
  filteredDevices,
  showSection,
  openStaffModal,
  openResidentModal,
  openFamilyModal,
  openFamilyModalForResident,
  openFamilyUserModal,
  closeModal,
  syncFamilyResidentLink,
  syncFamilyUserResidentLink,
  familyCountForResident,
  isAssignedDevice,
  availableDeviceOptions,
  saveModal,
  toggleFamilyState,
  formatDate,
  copyInviteLink,
  updateInviteState
} = useUsersManagement()

const isSaving = ref(false)
const validationMessage = ref('')
const saveAttempt = ref(0)
const toastMessage = ref('')
let toastTimer = null

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const trimValue = (value) => String(value ?? '').trim()

const isEmailValid = (value) => emailPattern.test(trimValue(value))

const isModalValid = computed(() => {
  if (modal.value.type === 'staff') {
    return Boolean(trimValue(staffForm.value.name) && isEmailValid(staffForm.value.email))
  }

  if (modal.value.type === 'resident') {
    return Boolean(trimValue(residentForm.value.name))
  }

  if (modal.value.type === 'family') {
    return Boolean(trimValue(familyForm.value.name) && isEmailValid(familyForm.value.email) && trimValue(familyForm.value.residentId))
  }

  if (modal.value.type === 'family-user') {
    return Boolean(trimValue(familyUserForm.value.name) && isEmailValid(familyUserForm.value.email) && trimValue(familyUserForm.value.residentId))
  }

  return false
})

const getValidationMessage = () => {
  if (modal.value.type === 'staff') {
    return 'Please enter a valid name and email for the staff member.'
  }

  if (modal.value.type === 'resident') {
    return 'Please enter the resident name.'
  }

  if (modal.value.type === 'family') {
    return 'Please enter the family name, a valid email and a resident.'
  }

  if (modal.value.type === 'family-user') {
    return 'Please enter the family user name, a valid email and a resident.'
  }

  return 'Please complete the required fields.'
}

const handleSaveModal = async () => {
  if (isSaving.value) {
    return
  }

  saveAttempt.value += 1

  if (!isModalValid.value) {
    validationMessage.value = getValidationMessage()
    return
  }

  validationMessage.value = ''
  isSaving.value = true
  const modalType = modal.value.type

  try {
    await saveModal()
    toastMessage.value = getSuccessMessage(modalType)
    if (toastTimer) {
      clearTimeout(toastTimer)
    }
    toastTimer = window.setTimeout(() => {
      toastMessage.value = ''
    }, 2500)
  } finally {
    isSaving.value = false
  }
}

const getSuccessMessage = (modalType) => {
  if (modalType === 'staff') {
    return 'Staff member saved successfully.'
  }

  if (modalType === 'resident') {
    return 'Resident saved successfully.'
  }

  if (modalType === 'family') {
    return 'Family invite created successfully.'
  }

  return 'Family user updated successfully.'
}

watch(
  () => modal.value.type,
  (modalType) => {
    if (!modalType) {
      validationMessage.value = ''
      saveAttempt.value = 0
    }
  }
)

watch(isModalValid, (isValid) => {
  if (isValid) {
    validationMessage.value = ''
  }
})

onBeforeUnmount(() => {
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
})
</script>

<style scoped>
.users-page {
  display: grid;
}

.users-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}

.toast {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  max-width: 100%;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid rgba(16, 185, 129, 0.18);
  background: rgba(236, 253, 245, 0.92);
  color: #047857;
  font-size: 0.86rem;
  font-weight: 700;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.05);
}

.page-eyebrow,
.section-eyebrow {
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
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--text-main);
}

.page-subtitle {
  margin: 8px 0 0;
  max-width: 760px;
  color: var(--text-muted);
  line-height: 1.6;
}

.page-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid transparent;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease, background 0.2s ease;
}

.action-button:hover {
  transform: translateY(-1px);
}

.action-button--primary {
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  color: #ffffff;
  box-shadow: 0 14px 30px rgba(37, 89, 189, 0.18);
}

.action-button--secondary {
  background: var(--surface-panel-strong);
  color: #2559bd;
  border-color: var(--surface-border);
}

.action-button--soft {
  background: var(--surface-panel-strong);
  color: #047857;
  border-color: var(--surface-border);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  padding: 20px;
  border-radius: 24px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 14px 34px var(--surface-shadow);
}

.summary-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.summary-value {
  display: block;
  margin: 10px 0 10px;
  font-size: clamp(1.8rem, 2.8vw, 2.5rem);
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: var(--text-main);
}

.summary-meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.5;
}

.toolbar-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel);
  box-shadow: 0 14px 30px var(--surface-shadow);
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tab {
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: var(--text-main);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.tab:hover {
  transform: translateY(-1px);
}

.tab.active {
  color: #93c5fd;
  background: rgba(37, 99, 235, 0.18);
  border-color: rgba(59, 130, 246, 0.24);
}

.search-field {
  position: relative;
  flex: 1 1 360px;
  max-width: 440px;
}

.search-field__icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(100, 116, 139, 0.72);
  font-size: 1.1rem;
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

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.section-card {
  padding: 18px;
  border-radius: 24px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  box-shadow: 0 14px 34px var(--surface-shadow);
}


.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.section-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 900;
  color: var(--text-main);
}

.section-action {
  padding: 10px 14px;
  border-radius: 14px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: var(--text-main);
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.section-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(37, 89, 189, 0.08);
}

.section-count {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.stack {
  display: grid;
  gap: 10px;
}

.entry-row,
.entry-card,
.table-row {
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
}

.entry-row {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.entry-row--staff {
  background: var(--surface-panel-strong);
}

.entry-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #00327d, #0047ab);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 900;
}

.entry-main {
  min-width: 0;
}

.entry-name {
  display: inline-block;
  color: var(--text-main);
  font-size: 1rem;
  line-height: 1.2;
  margin-bottom: 2px;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.entry-meta,
.entry-note {
  color: var(--text-muted);
  font-size: 0.84rem;
}

.label-strong {
  color: var(--text-main);
  font-weight: 800;
}

.block {
  display: block;
  margin-top: 3px;
}

.entry-link {
  border: none;
  background: transparent;
  color: #2559bd;
  font-weight: 800;
  cursor: pointer;
  padding: 0;
}

.entry-link--danger {
  color: #ef4444;
}

.entry-card {
  display: grid;
  gap: 10px;
}

.entry-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.entry-inline,
.entry-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.entry-actions {
  justify-content: flex-end;
}

.entry-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.24);
  font-size: 0.76rem;
  font-weight: 800;
}

.entry-chip--link {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pill--success {
  background: rgba(16, 185, 129, 0.18);
  color: #6ee7b7;
}

.pill--warning {
  background: rgba(249, 115, 22, 0.18);
  color: #fdba74;
}

.table-card {
  display: grid;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--surface-border);
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.table-head {
  padding: 12px 14px;
  background: var(--surface-panel-strong);
  color: var(--text-muted);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 900;
}

.table-row {
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.table-row--empty {
  grid-template-columns: 1fr;
  justify-items: center;
}

.empty-card {
  justify-items: center;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
}

.table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.admin-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #64748b;
  background: rgba(248, 250, 252, 0.8);
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  white-space: nowrap;
}

.admin-table th:first-child { border-top-left-radius: 16px; }
.admin-table th:last-child { border-top-right-radius: 16px; text-align: center; }

.admin-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  color: var(--text-main);
  vertical-align: middle;
}

.admin-table td:last-child { text-align: center; }

.admin-table tbody tr {
  transition: background 0.2s ease;
}

.admin-table tbody tr:hover {
  background: rgba(248, 250, 252, 0.75);
}

.admin-table__empty td {
  padding: 28px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.cell-name {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.cell-name strong { font-size: 0.96rem; font-weight: 800; }
.cell-name span { font-size: 0.8rem; color: var(--text-muted); }

.cell-avatar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.avatar-circle {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #00327d, #0047ab);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 900;
  flex-shrink: 0;
}

.cell-actions {
  display: inline-flex;
  gap: 12px;
  justify-content: center;
}

:global(.dark-mode) .admin-table th {
  background: rgba(15, 23, 42, 0.6);
  color: #94a3b8;
  border-bottom-color: rgba(51, 65, 85, 0.5);
}

:global(.dark-mode) .admin-table td {
  border-bottom-color: rgba(51, 65, 85, 0.3);
}

:global(.dark-mode) .admin-table tbody tr:hover {
  background: rgba(30, 41, 59, 0.4);
}

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .page-header {
    align-items: flex-start;
  }

  .page-actions {
    width: 100%;
  }

  .action-button {
    flex: 1 1 0;
  }

  .toolbar-panel {
    align-items: stretch;
  }

  .search-field {
    max-width: none;
    flex: 1 1 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .entry-row {
    grid-template-columns: 1fr;
  }

  .table-head,
  .table-row {
    grid-template-columns: 1fr;
  }

  .entry-card__head {
    flex-direction: column;
  }

  .entry-actions {
    justify-content: flex-start;
  }
}
</style>
