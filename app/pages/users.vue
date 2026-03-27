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
              <span class="meta block">{{ member.role }} · {{ member.area }}</span>
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

    <div v-if="modal.type" class="modal-backdrop" @click.self="closeModal">
      <div class="modal panel">
        <div class="section-head">
          <h3>{{ modalTitle }}</h3>
          <button class="link-btn" @click="closeModal">Close</button>
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
                {{ device.patientName }} · {{ device.deviceId }}
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
            <select v-model="familyForm.residentId" class="search" @change="syncFamilyResidentLink">
              <option value="">Select resident</option>
              <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}{{ resident.deviceId ? ` · ${resident.deviceId}` : '' }}
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
            <select v-model="familyUserForm.residentId" class="search" @change="syncFamilyUserResidentLink">
              <option value="">Select resident</option>
              <option v-for="resident in residents" :key="resident.id" :value="resident.id">
                {{ resident.name }}{{ resident.deviceId ? ` · ${resident.deviceId}` : '' }}
              </option>
            </select>
          </label>
          <label class="field field-full">
            <span>Associated device</span>
            <select v-model="familyUserForm.deviceIdOverride" class="search">
              <option value="">Use resident device</option>
              <option v-for="device in devices" :key="device.id" :value="device.deviceId">
                {{ device.patientName }} · {{ device.deviceId }}
              </option>
            </select>
          </label>
        </div>

        <div class="actions">
          <button class="btn btn-muted" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="saveModal">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'
import { PERMISSIONS } from '~/utils/permissions'

const auth = useAuthStore()
const search = ref('')
const activeTab = ref('all')
const modal = ref({ type: '' })

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'staff', label: 'Staff' },
  { id: 'residents', label: 'Residents' },
  { id: 'family', label: 'Family' },
  { id: 'invitations', label: 'Invitations' },
  { id: 'devices', label: 'Beds' }
]

const staffRoles = ['Call Center Admin', 'Clinical Staff', 'Technical Operator']
const staffAreas = ['Floor 1', 'ICU', 'Recovery', 'Devices']

const { data: staffData, refresh: refreshStaff } = await useFetch('http://localhost:5000/staff-members', {
  server: false,
  default: () => []
})

const { data: residentsData, refresh: refreshResidents } = await useFetch('http://localhost:5000/residents', {
  server: false,
  default: () => []
})

const staffMembers = computed(() => Array.isArray(staffData.value) ? staffData.value : [])
const residents = computed(() => Array.isArray(residentsData.value) ? residentsData.value : [])

const { data: devicesData, pending: resourcesLoading } = await useFetch('http://localhost:5000/devices', {
  server: false,
  default: () => []
})

const { data: familyUsersData, refresh: refreshFamilyUsers } = await useFetch('http://localhost:5000/family-users', {
  server: false,
  default: () => []
})

const { data: invitesData, refresh: refreshInvites } = await useFetch('http://localhost:5000/invites', {
  server: false,
  default: () => []
})

const devices = computed(() =>
  (Array.isArray(devicesData.value) ? devicesData.value : []).map((device, index) => {
    const deviceId = device.id || ''
    return {
      id: deviceId || index + 1,
      patientName: device.name || `Bed ${String(deviceId).slice(-5)}`,
      deviceId,
      status: device.type || 'Registered'
    }
  })
)

const sameId = (a, b) => String(a ?? '') === String(b ?? '')
const findResidentById = (residentId) => residents.value.find(resident => sameId(resident.id, residentId))

const familyAccounts = computed(() =>
  (Array.isArray(familyUsersData.value) ? familyUsersData.value : []).map((user, index) => {
    const linkedResident = residents.value.find(resident =>
      sameId(resident.id, user.residentId) || resident.name === user.patientName
    )

    return {
      id: user.id || index + 1,
      residentId: user.residentId || linkedResident?.id || null,
      name: user.name || 'Unknown user',
      email: user.email || '',
      patientName: linkedResident?.name || user.patientName || 'Unassigned',
      deviceId: user.deviceIdOverride || linkedResident?.deviceId || user.deviceId || '',
      relationship: user.relationship || 'Family',
      state: user.state || 'Active',
      deviceIdOverride: user.deviceIdOverride || ''
    }
  })
)

const invitations = computed(() =>
  (Array.isArray(invitesData.value) ? invitesData.value : []).map((invite, index) => ({
    id: invite.id || index + 1,
    email: invite.email || '',
    name: invite.name || '',
    patientName: invite.patientName || 'Unassigned',
    relationship: invite.relationship || '',
    residentId: invite.residentId || null,
    deviceId: invite.deviceId || '',
    state: String(invite.state || 'PENDING').toUpperCase(),
    createdAt: invite.createdAt || '',
    expiresAt: invite.expiresAt || '',
    acceptedAt: invite.acceptedAt || null,
    cancelledAt: invite.cancelledAt || null,
    acceptUrl: invite.acceptUrl || '',
    stateLabel: String(invite.state || 'PENDING').toUpperCase(),
    stateClass: ['ACCEPTED'].includes(String(invite.state || '').toUpperCase())
      ? 'ok'
      : ['EXPIRED', 'CANCELLED'].includes(String(invite.state || '').toUpperCase())
        ? 'danger'
        : 'warn'
  }))
)

const staffForm = ref({ id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] })
const residentForm = ref({ id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' })
const familyForm = ref({ id: null, residentId: '', name: '', email: '', relationship: '', state: 'Pending', patientName: 'Unassigned', deviceId: '' })
const familyUserForm = ref({ id: null, residentId: '', name: '', email: '', relationship: '', state: 'Active', patientName: 'Unassigned', deviceId: '', deviceIdOverride: '' })

const query = computed(() => search.value.trim().toLowerCase())
const canCreateRecords = computed(() => auth.permissions.includes(PERMISSIONS.USER_CREATE_RECORDS))
const matchesSearch = (values) => !query.value || values.some(value => String(value).toLowerCase().includes(query.value))
const showSection = (section) => activeTab.value === 'all' || activeTab.value === section

const filteredStaff = computed(() =>
  staffMembers.value.filter(member => matchesSearch([member.name, member.email, member.role, member.area]))
)

const filteredResidents = computed(() =>
  residents.value.filter(resident => matchesSearch([resident.name, resident.deviceId, resident.status, resident.notes]))
)

const filteredFamilies = computed(() =>
  familyAccounts.value.filter(relative =>
    matchesSearch([relative.name, relative.email, relative.patientName, relative.deviceId, relative.relationship])
  )
)

const filteredInvitations = computed(() =>
  invitations.value.filter(invite =>
    matchesSearch([invite.email, invite.name, invite.patientName, invite.relationship, invite.state, invite.deviceId])
  )
)

const filteredDevices = computed(() =>
  devices.value.filter(device => matchesSearch([device.patientName, device.deviceId, device.status]))
)

const assignedDeviceIds = computed(() => new Set(residents.value.map(resident => resident.deviceId).filter(Boolean)))
const activeFamilies = computed(() => familyAccounts.value.length)
const pendingInvitations = computed(() => invitations.value.filter(invite => invite.state === 'PENDING').length)
const assignedResidents = computed(() => residents.value.filter(item => item.deviceId).length)
const availableBeds = computed(() => devices.value.filter(device => !assignedDeviceIds.value.has(device.deviceId)).length)

const summaryCards = computed(() => [
  { label: 'Staff', value: staffMembers.value.length, meta: 'Registered users' },
  { label: 'Residents', value: residents.value.length, meta: `${assignedResidents.value} with assigned bed` },
  { label: 'Families', value: activeFamilies.value, meta: 'Registered family users' },
  { label: 'Invites', value: pendingInvitations.value, meta: 'Pending invitations' },
  { label: 'Beds', value: devices.value.length, meta: `${availableBeds.value} available` }
])

const modalTitle = computed(() => {
  if (modal.value.type === 'staff') return staffForm.value.id ? 'Edit Staff' : 'Create Staff'
  if (modal.value.type === 'resident') return residentForm.value.id ? 'Edit Resident' : 'Create Resident'
  if (modal.value.type === 'family') return familyForm.value.id ? 'Edit Family Access' : 'Invite Family'
  return 'Edit Family User'
})

const resetForms = () => {
  staffForm.value = { id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] }
  residentForm.value = { id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' }
  familyForm.value = { id: null, residentId: '', name: '', email: '', relationship: '', state: 'Pending', patientName: 'Unassigned', deviceId: '' }
  familyUserForm.value = { id: null, residentId: '', name: '', email: '', relationship: '', state: 'Active', patientName: 'Unassigned', deviceId: '', deviceIdOverride: '' }
}

const openStaffModal = (member = null) => {
  if (!member && !canCreateRecords.value) return
  staffForm.value = member ? { ...member } : { id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] }
  modal.value = { type: 'staff' }
}

const openResidentModal = (resident = null) => {
  if (!resident && !canCreateRecords.value) return
  residentForm.value = resident ? { ...resident } : { id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' }
  modal.value = { type: 'resident' }
}

const openFamilyModal = (relative = null) => {
  if (!relative && !canCreateRecords.value) return
  familyForm.value = relative
    ? { ...relative, residentId: relative.residentId || '' }
    : { id: null, residentId: '', name: '', email: '', relationship: '', state: 'Pending', patientName: 'Unassigned', deviceId: '' }
  modal.value = { type: 'family' }
}

const openFamilyModalForResident = (resident) => {
  openFamilyModal()
  familyForm.value.residentId = resident.id
  syncFamilyResidentLink()
}

const openFamilyUserModal = (relative) => {
  familyUserForm.value = {
    id: relative.id,
    residentId: relative.residentId || '',
    name: relative.name || '',
    email: relative.email || '',
    relationship: relative.relationship || '',
    state: relative.state || 'Active',
    patientName: relative.patientName || 'Unassigned',
    deviceId: relative.deviceId || '',
    deviceIdOverride: relative.deviceIdOverride || ''
  }
  modal.value = { type: 'family-user' }
}

const closeModal = () => {
  modal.value = { type: '' }
  resetForms()
}

const syncFamilyResidentLink = () => {
  const resident = findResidentById(familyForm.value.residentId)
  familyForm.value.patientName = resident?.name || 'Unassigned'
  familyForm.value.deviceId = resident?.deviceId || ''
}

const syncFamilyUserResidentLink = () => {
  const resident = findResidentById(familyUserForm.value.residentId)
  familyUserForm.value.patientName = resident?.name || 'Unassigned'
  familyUserForm.value.deviceId = resident?.deviceId || ''
  familyUserForm.value.deviceIdOverride = ''
}

const familyCountForResident = (residentName) =>
  familyAccounts.value.filter(relative => relative.patientName === residentName).length

const isAssignedDevice = (deviceId) => assignedDeviceIds.value.has(deviceId)

const availableDeviceOptions = (currentResidentId = null) => {
  const currentResident = findResidentById(currentResidentId)
  return devices.value.filter(device => {
    if (!isAssignedDevice(device.deviceId)) return true
    return currentResident?.deviceId === device.deviceId
  })
}

const saveStaff = () => {
  return saveStaffMember()
}

const saveResident = () => {
  return saveResidentRecord()
}

const saveFamily = () => {
  return saveFamilyInvite()
}

const saveModal = () => {
  if (modal.value.type === 'staff') saveStaff()
  else if (modal.value.type === 'resident') saveResident()
  else if (modal.value.type === 'family') saveFamily()
  else saveFamilyUser()
}

const toggleFamilyState = async (familyId) => {
  const familyUser = familyAccounts.value.find(relative => sameId(relative.id, familyId))
  if (!familyUser) return

  try {
    await $fetch(`http://localhost:5000/family-users/${familyUser.id}`, {
      method: 'PUT',
      body: {
        name: familyUser.name,
        email: familyUser.email,
        relationship: familyUser.relationship,
        residentId: familyUser.residentId,
        patientName: familyUser.patientName,
        deviceId: familyUser.deviceId,
        deviceIdOverride: familyUser.deviceIdOverride || '',
        state: familyUser.state === 'Active' ? 'Inactive' : 'Active'
      }
    })
    await refreshFamilyUsers()
  } catch (error) {
    console.error('Error updating family user state:', error)
    alert('Could not update the family user status.')
  }
}

const saveFamilyInvite = async () => {
  if (!canCreateRecords.value) {
    alert('You do not have permission to create invitations.')
    return
  }
  if (!familyForm.value.name || !familyForm.value.email) return

  const resident = findResidentById(familyForm.value.residentId)
  if (!resident) {
    alert('Selecciona un residente valido antes de crear la invitacion.')
    return
  }

  const payload = {
    ...familyForm.value,
    residentId: resident.id,
    patientName: resident.name,
    deviceId: resident.deviceId || '',
    state: 'Pending'
  }

  try {
    const invitation = await $fetch('http://localhost:5000/invites', {
      method: 'POST',
      body: payload
    })

    await refreshInvites()
    if (invitation?.acceptUrl && navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(invitation.acceptUrl)
      alert(`Invitation created. Link copied to clipboard:\n${invitation.acceptUrl}`)
    } else {
      alert(`Invitation created:\n${invitation?.acceptUrl || 'Link unavailable'}`)
    }
    closeModal()
  } catch (error) {
    console.error('Error creating invitation:', error)
    alert('No se pudo crear la invitacion.')
  }
}

const saveFamilyUser = async () => {
  if (!familyUserForm.value.id || !familyUserForm.value.name || !familyUserForm.value.email) return

  const resident = findResidentById(familyUserForm.value.residentId)
  const payload = {
    name: familyUserForm.value.name,
    email: familyUserForm.value.email,
    relationship: familyUserForm.value.relationship,
    state: familyUserForm.value.state,
    residentId: resident?.id || null,
    patientName: resident?.name || 'Unassigned',
    deviceId: resident?.deviceId || familyUserForm.value.deviceId || '',
    deviceIdOverride: familyUserForm.value.deviceIdOverride || ''
  }

  try {
    await $fetch(`http://localhost:5000/family-users/${familyUserForm.value.id}`, {
      method: 'PUT',
      body: payload
    })
    await refreshFamilyUsers()
    closeModal()
  } catch (error) {
    console.error('Error saving family user:', error)
    alert('Could not update the family user.')
  }
}

const saveStaffMember = async () => {
  if (!canCreateRecords.value && !staffForm.value.id) {
    alert('You do not have permission to create staff users.')
    return
  }
  if (!staffForm.value.name || !staffForm.value.email) return
  try {
    await $fetch('http://localhost:5000/staff-members', {
      method: 'POST',
      body: { ...staffForm.value }
    })
    await refreshStaff()
    closeModal()
  } catch (error) {
    console.error('Error saving staff member:', error)
    alert('No se pudo guardar el staff.')
  }
}

const saveResidentRecord = async () => {
  if (!canCreateRecords.value && !residentForm.value.id) {
    alert('You do not have permission to create residents.')
    return
  }
  if (!residentForm.value.name) return
  try {
    await $fetch('http://localhost:5000/residents', {
      method: 'POST',
      body: { ...residentForm.value }
    })
    await refreshResidents()
    await refreshFamilyUsers()
    await refreshInvites()
    closeModal()
  } catch (error) {
    console.error('Error saving resident:', error)
    alert('No se pudo guardar el residente.')
  }
}

const formatDate = (value) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

const copyInviteLink = async (acceptUrl) => {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(acceptUrl)
      alert('Invitation link copied.')
      return
    }
  } catch (error) {
    console.error('Could not copy invite link:', error)
  }
  alert(acceptUrl)
}

const updateInviteState = async (inviteId, state) => {
  try {
    await $fetch(`http://localhost:5000/invites/${inviteId}/state`, {
      method: 'PUT',
      body: { state }
    })
    await refreshInvites()
  } catch (error) {
    console.error('Error updating invitation state:', error)
    alert('Could not update invitation state.')
  }
}
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
