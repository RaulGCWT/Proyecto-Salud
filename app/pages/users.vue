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

          <div class="stack">
            <div v-for="member in filteredStaff" :key="member.id" class="entry-row entry-row--staff">
              <div class="entry-avatar">{{ member.name.charAt(0) }}</div>
              <div class="entry-main">
                <strong class="entry-name">{{ member.name }}</strong>
                <span class="entry-meta block">{{ member.role }} - {{ member.area }}</span>
                <span class="entry-meta"><strong class="label-strong">Contact:</strong> {{ member.email }}</span>
              </div>
              <button class="entry-link" type="button" @click="openStaffModal(member)">Manage</button>
            </div>
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

          <div class="stack">
            <div v-for="resident in filteredResidents" :key="resident.id" class="entry-card">
              <div class="entry-card__head">
                <div>
                  <strong class="entry-name">{{ resident.name }}</strong>
                  <span class="entry-meta block"><strong class="label-strong">Status:</strong> {{ resident.status }}</span>
                </div>
                <code class="entry-chip"><strong class="label-strong">Bed:</strong> {{ resident.deviceId || 'Unassigned' }}</code>
              </div>

              <div class="entry-inline">
                <span class="entry-meta"><strong class="label-strong">Family linked:</strong> {{ familyCountForResident(resident.name) }}</span>
                <span class="entry-meta"><strong class="label-strong">Notes:</strong> {{ resident.notes || 'No notes' }}</span>
              </div>

              <div class="entry-actions">
                <button class="entry-link" type="button" @click="openResidentModal(resident)">Edit</button>
                <button v-if="canCreateRecords" class="entry-link" type="button" @click="openFamilyModalForResident(resident)">Invite Family</button>
              </div>
            </div>
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

          <div class="stack">
            <div v-for="relative in filteredFamilies" :key="relative.id" class="entry-card">
              <div class="entry-card__head">
                <div>
                  <strong class="entry-name">{{ relative.name }}</strong>
                  <span class="entry-meta block"><strong class="label-strong">Role:</strong> Family</span>
                  <span class="entry-meta block"><strong class="label-strong">Contact:</strong> {{ relative.email }}</span>
                </div>
                <span :class="['pill', relative.state === 'Active' ? 'pill--success' : 'pill--warning']">{{ relative.state }}</span>
              </div>

              <div class="entry-inline">
                <span class="entry-meta"><strong class="label-strong">Family of:</strong> {{ relative.patientName }}</span>
                <span class="entry-meta"><strong class="label-strong">Information:</strong> {{ relative.relationship }}</span>
              </div>

              <div v-if="relative.deviceId" class="entry-inline">
                <code class="entry-chip"><strong class="label-strong">Associated devices:</strong> {{ relative.deviceId }}</code>
              </div>

              <div class="entry-actions">
                <span class="entry-note">Registered family user</span>
                <button class="entry-link" type="button" @click="openFamilyUserModal(relative)">Edit</button>
                <button class="entry-link" type="button" @click="toggleFamilyState(relative.id)">
                  {{ relative.state === 'Active' ? 'Deactivate' : 'Activate' }}
                </button>
              </div>
            </div>
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

          <div class="stack">
            <div v-if="!filteredInvitations.length" class="entry-card empty-card">
              <span class="entry-note">No invitations match the current filter.</span>
            </div>

            <div v-for="invite in filteredInvitations" :key="invite.id" class="entry-card">
              <div class="entry-card__head">
                <div>
                  <strong class="entry-name">{{ invite.email }}</strong>
                  <span class="entry-meta block"><strong class="label-strong">Resident:</strong> {{ invite.patientName }}</span>
                  <span class="entry-meta block"><strong class="label-strong">Relationship:</strong> {{ invite.relationship || 'Family' }}</span>
                </div>
                <span :class="['pill', invite.stateClass]">{{ invite.stateLabel }}</span>
              </div>

              <div class="entry-inline">
                <span class="entry-meta"><strong class="label-strong">Created:</strong> {{ formatDate(invite.createdAt) }}</span>
                <span class="entry-meta"><strong class="label-strong">Expires:</strong> {{ formatDate(invite.expiresAt) }}</span>
              </div>

              <div v-if="invite.acceptUrl" class="entry-inline">
                <code class="entry-chip entry-chip--link">{{ invite.acceptUrl }}</code>
              </div>

              <div class="entry-actions">
                <button v-if="invite.acceptUrl" class="entry-link" type="button" @click="copyInviteLink(invite.acceptUrl)">Copy link</button>
                <button v-if="invite.state === 'PENDING'" class="entry-link entry-link--danger" type="button" @click="updateInviteState(invite.id, 'CANCELLED')">Cancel</button>
                <button v-if="invite.state === 'CANCELLED' || invite.state === 'EXPIRED'" class="entry-link" type="button" @click="updateInviteState(invite.id, 'PENDING')">Reopen</button>
              </div>
            </div>
          </div>
        </article>

        <article v-if="showSection('devices')" class="section-card">
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Beds</p>
              <h2 class="section-title">Available Beds</h2>
            </div>
          </div>

          <div class="table-card">
            <div class="table-head">
              <span>Name</span>
              <span>Device</span>
              <span>Status</span>
            </div>

            <div v-if="resourcesLoading" class="table-row table-row--empty">
              <span class="entry-note">Loading devices...</span>
            </div>

            <div v-else-if="!filteredDevices.length" class="table-row table-row--empty">
              <span class="entry-note">No devices found in the database.</span>
            </div>

            <div v-else v-for="device in filteredDevices" :key="device.id" class="table-row">
              <strong>{{ device.patientName }}</strong>
              <code class="entry-chip">{{ device.deviceId }}</code>
              <span :class="['pill', isAssignedDevice(device.deviceId) ? 'pill--warning' : 'pill--success']">
                {{ isAssignedDevice(device.deviceId) ? 'Assigned' : 'Available' }}
              </span>
            </div>
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
  background: rgba(37, 89, 189, 0.08);
  color: #2559bd;
  border-color: rgba(37, 89, 189, 0.14);
}

.action-button--soft {
  background: rgba(16, 185, 129, 0.08);
  color: #047857;
  border-color: rgba(16, 185, 129, 0.14);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94));
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04);
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
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04);
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tab {
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(248, 250, 252, 0.92);
  color: #475569;
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
  color: #2559bd;
  background: rgba(37, 89, 189, 0.1);
  border-color: rgba(37, 89, 189, 0.18);
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
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: var(--bg-main);
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.section-card {
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94));
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04);
}

.section-card:nth-child(1),
.section-card:nth-child(2),
.section-card:nth-child(3),
.section-card:nth-child(4) {
  min-height: 0;
}

.section-card:nth-child(1),
.section-card:nth-child(2) {
  grid-column: span 1;
}

.section-card:nth-child(3),
.section-card:nth-child(4) {
  grid-column: span 1;
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
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(248, 250, 252, 0.92);
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
  background: rgba(37, 89, 189, 0.08);
  color: #2559bd;
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
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: #f8fafc;
}

.entry-row {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.entry-row--staff {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.96));
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
  background: rgba(37, 89, 189, 0.08);
  color: #2559bd;
  border: 1px solid rgba(37, 89, 189, 0.14);
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
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.pill--warning {
  background: rgba(249, 115, 22, 0.14);
  color: #ea580c;
}

.table-card {
  display: grid;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.12);
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
  background: rgba(248, 250, 252, 0.95);
  color: #64748b;
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

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
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
