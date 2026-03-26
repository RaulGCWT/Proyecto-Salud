<template>
  <div class="users-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">User Management</h1>
        <p class="page-subtitle">Flujo de gestion para staff, residentes, familiares y camas disponibles.</p>
      </div>

      <div class="actions">
        <button class="btn btn-muted" @click="openFamilyModal()">Invite Family</button>
        <button class="btn btn-secondary" @click="openResidentModal()">Create Resident</button>
        <button class="btn btn-primary" @click="openStaffModal()">Create Staff</button>
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
          <button class="btn btn-ghost" @click="openStaffModal()">New user</button>
        </div>

        <div class="stack">
          <div v-for="member in filteredStaff" :key="member.id" class="item-row">
            <div class="avatar">{{ member.name.charAt(0) }}</div>
            <div class="item-main">
              <strong>{{ member.name }}</strong>
              <span class="meta block">{{ member.role }} · {{ member.area }}</span>
              <span class="meta">{{ member.email }}</span>
            </div>
            <button class="link-btn" @click="openStaffModal(member)">Manage</button>
          </div>
        </div>
      </article>

      <article v-if="showSection('residents')" class="panel">
        <div class="section-head">
          <h3>Residents</h3>
          <button class="btn btn-ghost" @click="openResidentModal()">New resident</button>
        </div>

        <div class="stack">
          <div v-for="resident in filteredResidents" :key="resident.id" class="card-row">
            <div class="row-head">
              <div>
                <strong>{{ resident.name }}</strong>
                <span class="meta block">{{ resident.status }}</span>
              </div>
              <code class="tag">{{ resident.deviceId || 'Unassigned' }}</code>
            </div>

            <div class="row-inline">
              <span class="meta">Family linked: {{ familyCountForResident(resident.name) }}</span>
              <span class="meta">{{ resident.notes || 'No notes' }}</span>
            </div>

            <div class="row-actions">
              <button class="link-btn" @click="openResidentModal(resident)">Edit</button>
              <button class="link-btn" @click="openFamilyModalForResident(resident)">Invite Family</button>
            </div>
          </div>
        </div>
      </article>

      <article v-if="showSection('family')" class="panel">
        <div class="section-head">
          <h3>Family Access</h3>
          <button class="btn btn-ghost" @click="openFamilyModal()">Send invite</button>
        </div>

        <div class="stack">
          <div v-for="relative in filteredFamilies" :key="relative.id" class="card-row">
            <div class="row-head">
              <div>
                <strong>{{ relative.name }}</strong>
                <span class="meta block">{{ relative.email }}</span>
              </div>
              <span :class="['pill', relative.state === 'Active' ? 'ok' : 'warn']">{{ relative.state }}</span>
            </div>

            <div class="row-inline">
              <span>{{ relative.patientName }}</span>
              <code v-if="relative.deviceId" class="tag">{{ relative.deviceId }}</code>
              <span class="meta">{{ relative.relationship }}</span>
            </div>

            <div class="row-actions">
              <button class="link-btn" @click="openFamilyModal(relative)">Edit</button>
              <button class="link-btn danger" @click="removeFamily(relative.id)">Remove</button>
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

        <div v-else class="form-grid">
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

        <div class="actions">
          <button class="btn btn-muted" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="saveModal">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const search = ref('')
const activeTab = ref('all')
const modal = ref({ type: '' })
const nextStaffId = ref(5)
const nextResidentId = ref(4)
const nextFamilyId = ref(5)

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'staff', label: 'Staff' },
  { id: 'residents', label: 'Residents' },
  { id: 'family', label: 'Family' },
  { id: 'devices', label: 'Beds' }
]

const staffRoles = ['Call Center Admin', 'Clinical Staff', 'Technical Operator']
const staffAreas = ['Floor 1', 'ICU', 'Recovery', 'Devices']

const staffMembers = ref([
  { id: 1, name: 'Marta Lozano', role: 'Call Center Admin', area: 'Floor 1', email: 'marta.lozano@health.local' },
  { id: 2, name: 'Diego Perez', role: 'Clinical Staff', area: 'ICU', email: 'diego.perez@health.local' },
  { id: 3, name: 'Lucia Martin', role: 'Clinical Staff', area: 'Recovery', email: 'lucia.martin@health.local' },
  { id: 4, name: 'Carlos Vega', role: 'Technical Operator', area: 'Devices', email: 'carlos.vega@health.local' }
])

const residents = ref([
  { id: 1, name: 'Jose Robles', deviceId: 'BED-201-AF12', status: 'Active', notes: 'Linked to family access' },
  { id: 2, name: 'Elena Ruiz', deviceId: 'BED-114-CD45', status: 'Monitoring', notes: '' },
  { id: 3, name: 'Carmen Moreno', deviceId: 'BED-203-QW77', status: 'Active', notes: '' }
])

const familyAccounts = ref([
  { id: 1, residentId: 1, name: 'Ana Robles', email: 'ana.robles@mail.com', patientName: 'Jose Robles', deviceId: 'BED-201-AF12', relationship: 'Daughter', state: 'Active' },
  { id: 2, residentId: 2, name: 'Daniel Ruiz', email: 'daniel.ruiz@mail.com', patientName: 'Elena Ruiz', deviceId: 'BED-114-CD45', relationship: 'Son', state: 'Active' },
  { id: 3, residentId: null, name: 'Sofia Leon', email: 'sofia.leon@mail.com', patientName: 'Unassigned', deviceId: '', relationship: 'Sister', state: 'Pending' },
  { id: 4, residentId: 3, name: 'Paula Moreno', email: 'paula.moreno@mail.com', patientName: 'Carmen Moreno', deviceId: 'BED-203-QW77', relationship: 'Spouse', state: 'Active' }
])

const { data: devicesData, pending: resourcesLoading } = await useFetch('http://localhost:5000/devices', {
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

const staffForm = ref({ id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] })
const residentForm = ref({ id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' })
const familyForm = ref({ id: null, residentId: '', name: '', email: '', relationship: '', state: 'Pending', patientName: 'Unassigned', deviceId: '' })

const query = computed(() => search.value.trim().toLowerCase())
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

const filteredDevices = computed(() =>
  devices.value.filter(device => matchesSearch([device.patientName, device.deviceId, device.status]))
)

const assignedDeviceIds = computed(() => new Set(residents.value.map(resident => resident.deviceId).filter(Boolean)))
const activeFamilies = computed(() => familyAccounts.value.filter(item => item.state === 'Active').length)
const assignedResidents = computed(() => residents.value.filter(item => item.deviceId).length)
const availableBeds = computed(() => devices.value.filter(device => !assignedDeviceIds.value.has(device.deviceId)).length)

const summaryCards = computed(() => [
  { label: 'Staff', value: staffMembers.value.length, meta: 'Registered users' },
  { label: 'Residents', value: residents.value.length, meta: `${assignedResidents.value} with assigned bed` },
  { label: 'Families', value: activeFamilies.value, meta: `${familyAccounts.value.length} invitations total` },
  { label: 'Beds', value: devices.value.length, meta: `${availableBeds.value} available` }
])

const modalTitle = computed(() => {
  if (modal.value.type === 'staff') return staffForm.value.id ? 'Edit Staff' : 'Create Staff'
  if (modal.value.type === 'resident') return residentForm.value.id ? 'Edit Resident' : 'Create Resident'
  return familyForm.value.id ? 'Edit Family Access' : 'Invite Family'
})

const resetForms = () => {
  staffForm.value = { id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] }
  residentForm.value = { id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' }
  familyForm.value = { id: null, residentId: '', name: '', email: '', relationship: '', state: 'Pending', patientName: 'Unassigned', deviceId: '' }
}

const openStaffModal = (member = null) => {
  staffForm.value = member ? { ...member } : { id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] }
  modal.value = { type: 'staff' }
}

const openResidentModal = (resident = null) => {
  residentForm.value = resident ? { ...resident } : { id: null, name: '', deviceId: '', status: 'Pending Setup', notes: '' }
  modal.value = { type: 'resident' }
}

const openFamilyModal = (relative = null) => {
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

const closeModal = () => {
  modal.value = { type: '' }
  resetForms()
}

const syncFamilyResidentLink = () => {
  const resident = residents.value.find(item => item.id === Number(familyForm.value.residentId))
  familyForm.value.patientName = resident?.name || 'Unassigned'
  familyForm.value.deviceId = resident?.deviceId || ''
}

const familyCountForResident = (residentName) =>
  familyAccounts.value.filter(relative => relative.patientName === residentName).length

const isAssignedDevice = (deviceId) => assignedDeviceIds.value.has(deviceId)

const availableDeviceOptions = (currentResidentId = null) => {
  const currentResident = residents.value.find(item => item.id === currentResidentId)
  return devices.value.filter(device => {
    if (!isAssignedDevice(device.deviceId)) return true
    return currentResident?.deviceId === device.deviceId
  })
}

const saveStaff = () => {
  if (!staffForm.value.name || !staffForm.value.email) return
  if (staffForm.value.id) {
    const index = staffMembers.value.findIndex(item => item.id === staffForm.value.id)
    if (index !== -1) staffMembers.value[index] = { ...staffForm.value }
  } else {
    staffMembers.value.unshift({ ...staffForm.value, id: nextStaffId.value++ })
  }
  closeModal()
}

const saveResident = () => {
  if (!residentForm.value.name) return
  if (residentForm.value.id) {
    const index = residents.value.findIndex(item => item.id === residentForm.value.id)
    if (index !== -1) residents.value[index] = { ...residentForm.value }
  } else {
    residents.value.unshift({ ...residentForm.value, id: nextResidentId.value++ })
  }

  familyAccounts.value = familyAccounts.value.map(relative =>
    relative.residentId === residentForm.value.id
      ? { ...relative, patientName: residentForm.value.name, deviceId: residentForm.value.deviceId }
      : relative
  )

  closeModal()
}

const saveFamily = () => {
  if (!familyForm.value.name || !familyForm.value.email) return
  const resident = residents.value.find(item => item.id === Number(familyForm.value.residentId))
  const payload = {
    ...familyForm.value,
    residentId: resident?.id || null,
    patientName: resident?.name || 'Unassigned',
    deviceId: resident?.deviceId || ''
  }

  if (payload.id) {
    const index = familyAccounts.value.findIndex(item => item.id === payload.id)
    if (index !== -1) familyAccounts.value[index] = payload
  } else {
    familyAccounts.value.unshift({ ...payload, id: nextFamilyId.value++ })
  }
  closeModal()
}

const saveModal = () => {
  if (modal.value.type === 'staff') saveStaff()
  else if (modal.value.type === 'resident') saveResident()
  else saveFamily()
}

const removeFamily = (id) => {
  familyAccounts.value = familyAccounts.value.filter(item => item.id !== id)
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
.summary-grid { grid-template-columns: repeat(4, 1fr); margin-bottom: 1.25rem; }
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
.item-row { display: grid; grid-template-columns: 42px 1fr auto; gap: 12px; align-items: center; }
.item-row, .card-row, .table-row, .bed-option { padding: 12px; }
.avatar { width: 42px; height: 42px; border-radius: 10px; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.item-main { min-width: 0; }
.meta { font-size: .84rem; }
.block { display: block; margin-top: 3px; }
.pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 9px; border-radius: 999px; font-size: .75rem; font-weight: 700; }
.pill.ok { background: rgba(16,185,129,.15); color: #10b981; }
.pill.warn { background: rgba(249,115,22,.14); color: #ea580c; }
.link-btn { border: none; background: transparent; color: #3b82f6; padding: 0; }
.link-btn.danger { color: #ef4444; }
.row-inline, .row-actions { margin-top: 10px; flex-wrap: wrap; }
.row-actions { justify-content: flex-end; }
.tag { font-size: .75rem; color: var(--text-main); background: var(--bg-card); padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border-color); }
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
@media (max-width: 1024px) { .summary-grid, .content-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 820px) {
  .page-header, .toolbar, .row-head, .table-head, .table-row { flex-direction: column; align-items: flex-start; }
  .summary-grid, .content-grid, .form-grid { grid-template-columns: 1fr; }
  .item-row { grid-template-columns: 1fr; }
  .search { max-width: none; }
  .row-actions { justify-content: flex-start; }
}
</style>
