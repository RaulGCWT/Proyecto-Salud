<template>
  <div class="users-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">User Management</h1>
        <p class="page-subtitle">Flujo de gestion para staff, residentes, familiares y camas disponibles.</p>
      </div>

      <div class="actions">
        <button v-if="canCreateRecords" class="btn btn-muted" @click="openFamilyModal()">Invite Family</button>
        <button v-if="canCreateRecords" class="btn btn-secondary" @click="openResidentModal()">Create Resident</button>
        <button v-if="canCreateRecords" class="btn btn-primary" @click="openStaffModal()">Create Staff</button>
      </div>
    </header>

    <section class="summary-grid">
      <article v-for="item in summaryCards" :key="item.label" class="panel stat-card">
        <span class="eyebrow">{{ item.label }}</span>
        <strong class="stat-value">{{ item.value }}</strong>
        <span class="meta">{{ item.meta }}</span>
      </article>
    </section>

    <section class="panel toolbar">
      <input v-model="search" class="search" type="text" placeholder="Search by user, resident, family or device..." />

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </section>

    <section class="content-grid">
      <article v-if="showSection('staff')" class="panel">
        <div class="section-head">
          <h3>Staff Team</h3>
          <button v-if="canCreateRecords" class="btn btn-ghost" @click="openStaffModal()">New user</button>
        </div>

        <div class="stack">
          <div v-for="member in filteredStaff" :key="member.id" class="item-row">
            <div class="avatar">{{ member.name.charAt(0) }}</div>
            <div class="item-main">
              <strong class="entity-name">{{ member.name }}</strong>
              <span class="meta block">{{ member.role }} - {{ member.area }}</span>
              <span class="meta"><strong class="label-strong">Contact:</strong> {{ member.email }}</span>
            </div>
            <button class="link-btn" @click="openStaffModal(member)">Manage</button>
          </div>
        </div>
      </article>

      <article v-if="showSection('residents')" class="panel">
        <div class="section-head">
          <h3>Residents</h3>
          <button v-if="canCreateRecords" class="btn btn-ghost" @click="openResidentModal()">New resident</button>
        </div>

        <div class="stack">
          <div v-for="resident in filteredResidents" :key="resident.id" class="card-row">
            <div class="row-head">
              <div>
                <strong class="entity-name">{{ resident.name }}</strong>
                <span class="meta block"><strong class="label-strong">Status:</strong> {{ resident.status }}</span>
              </div>
              <code class="tag"><strong class="label-strong">Bed:</strong> {{ resident.deviceId || 'Unassigned' }}</code>
            </div>

            <div class="row-inline">
              <span class="meta"><strong class="label-strong">Family linked:</strong> {{ familyCountForResident(resident.name) }}</span>
              <span class="meta"><strong class="label-strong">Notes:</strong> {{ resident.notes || 'No notes' }}</span>
            </div>

            <div class="row-actions">
              <button class="link-btn" @click="openResidentModal(resident)">Edit</button>
              <button v-if="canCreateRecords" class="link-btn" @click="openFamilyModalForResident(resident)">Invite Family</button>
            </div>
          </div>
        </div>
      </article>

      <article v-if="showSection('family')" class="panel">
        <div class="section-head">
          <h3>Family Access</h3>
          <button v-if="canCreateRecords" class="btn btn-ghost" @click="openFamilyModal()">Send invite</button>
        </div>

        <div class="stack">
          <div v-for="relative in filteredFamilies" :key="relative.id" class="card-row">
            <div class="row-head">
              <div>
                <strong class="family-name">{{ relative.name }}</strong>
                <span class="meta block"><strong class="label-strong">Role:</strong> Family</span>
                <span class="meta block"><strong class="label-strong">Contact:</strong> {{ relative.email }}</span>
              </div>
              <span :class="['pill', relative.state === 'Active' ? 'ok' : 'warn']">{{ relative.state }}</span>
            </div>

            <div class="row-inline">
              <span class="meta family-line"><strong class="label-strong">Family of:</strong> {{ relative.patientName }}</span>
              <span class="meta"><strong class="label-strong">Information:</strong> {{ relative.relationship }}</span>
            </div>

            <div v-if="relative.deviceId" class="row-inline">
              <code class="tag"><strong class="label-strong">Associated devices:</strong> {{ relative.deviceId }}</code>
            </div>

            <div class="row-actions">
              <span class="meta">Registered family user</span>
              <button class="link-btn" @click="openFamilyUserModal(relative)">Edit</button>
              <button class="link-btn" @click="toggleFamilyState(relative.id)">
                {{ relative.state === 'Active' ? 'Deactivate' : 'Activate' }}
              </button>
            </div>
          </div>
        </div>
      </article>

      <article v-if="showSection('invitations')" class="panel">
        <div class="section-head">
          <h3>Pending Invitations</h3>
          <span class="meta">{{ filteredInvitations.length }} visible</span>
        </div>

        <div class="stack">
          <div v-if="!filteredInvitations.length" class="card-row empty-card">
            <span class="meta">No invitations match the current filter.</span>
          </div>

          <div v-for="invite in filteredInvitations" :key="invite.id" class="card-row">
            <div class="row-head">
              <div>
                <strong class="family-name">{{ invite.email }}</strong>
                <span class="meta block"><strong class="label-strong">Resident:</strong> {{ invite.patientName }}</span>
                <span class="meta block"><strong class="label-strong">Relationship:</strong> {{ invite.relationship || 'Family' }}</span>
              </div>
              <span :class="['pill', invite.stateClass]">{{ invite.stateLabel }}</span>
            </div>

            <div class="row-inline">
              <span class="meta"><strong class="label-strong">Created:</strong> {{ formatDate(invite.createdAt) }}</span>
              <span class="meta"><strong class="label-strong">Expires:</strong> {{ formatDate(invite.expiresAt) }}</span>
            </div>

            <div v-if="invite.acceptUrl" class="row-inline">
              <code class="tag invitation-link">{{ invite.acceptUrl }}</code>
            </div>

            <div class="row-actions">
              <button v-if="invite.acceptUrl" class="link-btn" @click="copyInviteLink(invite.acceptUrl)">Copy link</button>
              <button v-if="invite.state === 'PENDING'" class="link-btn danger" @click="updateInviteState(invite.id, 'CANCELLED')">Cancel</button>
              <button v-if="invite.state === 'CANCELLED' || invite.state === 'EXPIRED'" class="link-btn" @click="updateInviteState(invite.id, 'PENDING')">Reopen</button>
            </div>
          </div>
        </div>
      </article>

      <article v-if="showSection('devices')" class="panel">
        <div class="section-head">
          <h3>Available Beds</h3>
        </div>

        <div class="table">
          <div class="table-head">
            <span>Name</span>
            <span>Device</span>
            <span>Status</span>
          </div>

          <div v-if="resourcesLoading" class="table-row empty-row">
            <span class="meta">Loading devices...</span>
          </div>

          <div v-else-if="!filteredDevices.length" class="table-row empty-row">
            <span class="meta">No devices found in the database.</span>
          </div>

          <div v-else v-for="device in filteredDevices" :key="device.id" class="table-row">
            <strong>{{ device.patientName }}</strong>
            <code class="tag">{{ device.deviceId }}</code>
            <span :class="['pill', isAssignedDevice(device.deviceId) ? 'warn' : 'ok']">
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
      :staff-roles="staffRoles"
      :staff-areas="staffAreas"
      :residents="residents"
      :devices="devices"
      :available-device-options="availableDeviceOptions"
      @close="closeModal"
      @save="saveModal"
      @family-resident-change="syncFamilyResidentLink"
      @family-user-resident-change="syncFamilyUserResidentLink"
    />
  </div>
</template>

<script setup>
import { useUsersManagement } from '~/composables/users/useUsersManagement'

const {
  search,
  activeTab,
  modal,
  tabs,
  staffRoles,
  staffAreas,
  staffMembers,
  residents,
  devices,
  familyAccounts,
  invitations,
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
</script>

<style scoped>
.users-page { max-width: 1280px; margin: 0 auto; }
.page-header, .toolbar, .section-head, .row-head, .row-inline, .table-head, .table-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.page-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
.page-title { margin: 0; font-size: 1.9rem; font-weight: 800; color: var(--text-main); }
.page-subtitle, .meta { color: var(--text-muted); }
.page-subtitle { margin: 6px 0 0; }
.actions, .tabs, .row-actions, .tags, .bed-options { display: flex; gap: 10px; flex-wrap: wrap; }
.summary-grid, .content-grid, .stack, .form-grid { display: grid; }
.summary-grid, .content-grid, .stack { gap: 16px; }
.summary-grid { grid-template-columns: repeat(5, 1fr); margin-bottom: 1.25rem; }
.content-grid { grid-template-columns: repeat(2, 1fr); }
.stack { gap: 10px; }
:is(.panel, .item-row, .card-row, .table-row, .bed-option) { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; }
.panel { padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,.08); }
.toolbar { margin-bottom: 1.25rem; }
.search { width: 100%; max-width: 420px; box-sizing: border-box; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-main); color: var(--text-main); outline: none; }
.btn, .tab, .link-btn { border-radius: 6px; font-weight: 600; cursor: pointer; transition: .2s ease; }
.btn, .tab { padding: 9px 12px; border: 1px solid var(--border-color); }
.btn-primary, .tab.active { background: #3b82f6; border-color: #3b82f6; color: white; }
.btn-secondary { background: #0f172a; border-color: #0f172a; color: white; }
.btn-muted, .btn-ghost, .tab { background: var(--bg-main); color: var(--text-main); }
.section-head { margin-bottom: 12px; }
.section-head h3 { margin: 0; color: var(--text-main); font-size: 1.05rem; }
.item-row { display: grid; grid-template-columns: 42px 1fr auto; gap: 12px; align-items: center; background: linear-gradient(180deg, var(--bg-card), color-mix(in srgb, var(--bg-card) 88%, var(--bg-main))); }
.item-row, .card-row, .table-row, .bed-option { padding: 12px; }
.avatar { width: 42px; height: 42px; border-radius: 10px; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.item-main { min-width: 0; }
.meta { font-size: .84rem; }
.label-strong { color: var(--text-main); font-weight: 700; }
.entity-name { display: inline-block; font-size: 1rem; line-height: 1.2; margin-bottom: 2px; text-decoration: underline; text-underline-offset: 3px; }
.item-main .block { margin-top: 4px; }
.item-main .meta:last-child { display: block; margin-top: 4px; }
.family-name { text-decoration: underline; text-underline-offset: 3px; }
.family-line { font-size: .84rem; }
.block { display: block; margin-top: 3px; }
.pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 9px; border-radius: 999px; font-size: .75rem; font-weight: 700; }
.pill.ok { background: rgba(16,185,129,.15); color: #10b981; }
.pill.warn { background: rgba(249,115,22,.14); color: #ea580c; }
.pill.danger { background: rgba(239,68,68,.14); color: #ef4444; }
.link-btn { border: none; background: transparent; color: #3b82f6; padding: 0; }
.link-btn.danger { color: #ef4444; }
.row-inline, .row-actions { margin-top: 10px; flex-wrap: wrap; }
.row-actions { justify-content: flex-end; }
.tag { font-size: .84rem; color: var(--text-main); background: var(--bg-card); padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border-color); }
.table { border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; }
.table-head { padding: 10px 12px; background: var(--bg-main); color: var(--text-muted); font-size: .75rem; text-transform: uppercase; font-weight: 700; }
.table-row { border-top: 1px solid var(--border-color); }
.empty-row { justify-content: center; }
.stat-value { display: block; color: var(--text-main); font-size: 1.7rem; line-height: 1; margin: 8px 0 6px; }
.eyebrow { font-size: .75rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, .45); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 1000; }
.modal { width: min(720px, 100%); }
.form-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; margin: 14px 0; }
.field { display: grid; gap: 6px; color: var(--text-main); font-size: .85rem; }
.field-full { grid-column: 1 / -1; }
.empty-card { justify-content: center; }
.invitation-link { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; }
@media (max-width: 1200px) { .summary-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 1024px) { .content-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 820px) {
  .page-header, .toolbar, .row-head, .table-head, .table-row { flex-direction: column; align-items: flex-start; }
  .summary-grid, .content-grid, .form-grid { grid-template-columns: 1fr; }
  .item-row { grid-template-columns: 1fr; }
  .search { max-width: none; }
  .row-actions { justify-content: flex-start; }
}
</style>
