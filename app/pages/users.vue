<template>
  <div class="users-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">User Management</h1>
        <p class="page-subtitle">Administracion de staff, familiares y recursos del tenant actual.</p>
      </div>

      <div class="actions">
        <button class="btn btn-muted" @click="openFamilyModal()">Invite Family</button>
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
      <input v-model="search" class="search" type="text" placeholder="Search by user, email or device..." />

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
      <article v-if="activeTab === 'all' || activeTab === 'staff'" class="panel">
        <div class="section-head">
          <h3>Staff Team</h3>
          <button class="btn btn-ghost" @click="openStaffModal()">New user</button>
        </div>

        <div class="stack">
          <div v-for="member in filteredStaff" :key="member.id" class="item-row">
            <div class="avatar">{{ member.name.charAt(0) }}</div>
            <div class="item-main">
              <div class="item-top">
                <strong>{{ member.name }}</strong>
              </div>
              <span class="meta">{{ member.role }} · {{ member.area }}</span>
              <span class="meta">{{ member.email }}</span>
            </div>
            <button class="link-btn" @click="openStaffModal(member)">Manage</button>
          </div>
        </div>
      </article>

      <article v-if="activeTab === 'all' || activeTab === 'family'" class="panel">
        <div class="section-head">
          <h3>Family Access</h3>
          <button class="btn btn-ghost" @click="openFamilyModal()">Send invite</button>
        </div>

        <div class="stack">
          <div v-for="relative in filteredFamilies" :key="relative.id" class="family-card">
            <div class="item-top">
              <div>
                <strong>{{ relative.name }}</strong>
                <span class="meta block">{{ relative.email }}</span>
              </div>
              <span :class="['pill', relative.state === 'Active' ? 'ok' : 'warn']">{{ relative.state }}</span>
            </div>

            <div class="family-link">
              <span>{{ relative.patientName }}</span>
              <div class="tags">
                <code v-for="bed in relative.beds" :key="bed" class="tag">{{ bed }}</code>
              </div>
              <span class="meta">{{ relative.relationship }}</span>
            </div>
            <div class="family-actions">
              <button class="link-btn" @click="openFamilyModal(relative)">Edit</button>
              <button class="link-btn danger" @click="removeFamily(relative.id)">Remove</button>
            </div>
          </div>
        </div>
      </article>

      <article v-if="activeTab === 'all' || activeTab === 'resources'" class="panel">
        <div class="section-head">
          <h3>Patient Resources</h3>
          <button class="btn btn-ghost" @click="activeTab = 'family'; openFamilyModal()">Assign device</button>
        </div>

        <div class="table">
          <div class="table-head">
            <span>Patient</span>
            <span>Device</span>
            <span>Status</span>
          </div>

          <div v-for="resource in filteredResources" :key="resource.id" class="table-row">
            <div>
              <strong>{{ resource.patientName }}</strong>
            </div>
            <code class="tag">{{ resource.deviceId }}</code>
            <span :class="['pill', resource.status === 'Occupied' ? 'warn' : 'ok']">{{ resource.status }}</span>
          </div>
        </div>
      </article>
    </section>

    <div v-if="modal.type" class="modal-backdrop" @click.self="closeModal">
      <div class="modal panel">
        <div class="section-head">
          <h3>{{ modal.type === 'staff' ? (staffForm.id ? 'Edit Staff' : 'Create Staff') : (familyForm.id ? 'Edit Family Access' : 'Invite Family') }}</h3>
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
            <span>Patient</span>
            <input v-model="familyForm.patientName" class="search" type="text" />
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
          <div class="field field-full">
            <span>Assigned beds</span>
            <div class="bed-options">
              <label v-for="resource in patientResources" :key="resource.id" class="bed-option">
                <input
                  :checked="familyForm.beds.includes(resource.deviceId)"
                  type="checkbox"
                  @change="toggleAssignedBed(resource.deviceId)"
                />
                <span>{{ resource.patientName }}</span>
                <code class="tag">{{ resource.deviceId }}</code>
              </label>
            </div>
          </div>
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
const nextFamilyId = ref(5)

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'staff', label: 'Staff' },
  { id: 'family', label: 'Family' },
  { id: 'resources', label: 'Resources' }
]

const staffRoles = [
  'Call Center Admin',
  'Clinical Staff',
  'Technical Operator'
]

const staffAreas = [
  'Floor 1',
  'ICU',
  'Recovery',
  'Devices'
]

const staffMembers = ref([
  { id: 1, name: 'Marta Lozano', role: 'Call Center Admin', area: 'Floor 1', email: 'marta.lozano@health.local' },
  { id: 2, name: 'Diego Perez', role: 'Clinical Staff', area: 'ICU', email: 'diego.perez@health.local' },
  { id: 3, name: 'Lucia Martin', role: 'Clinical Staff', area: 'Recovery', email: 'lucia.martin@health.local' },
  { id: 4, name: 'Carlos Vega', role: 'Technical Operator', area: 'Devices', email: 'carlos.vega@health.local' }
])

const familyAccounts = ref([
  { id: 1, name: 'Ana Robles', email: 'ana.robles@mail.com', patientName: 'Jose Robles', beds: ['BED-201-AF12'], relationship: 'Daughter', state: 'Active' },
  { id: 2, name: 'Daniel Ruiz', email: 'daniel.ruiz@mail.com', patientName: 'Elena Ruiz', beds: ['BED-114-CD45'], relationship: 'Son', state: 'Active' },
  { id: 3, name: 'Sofia Leon', email: 'sofia.leon@mail.com', patientName: 'Antonio Leon', beds: ['BED-317-ZX90'], relationship: 'Sister', state: 'Pending' },
  { id: 4, name: 'Paula Moreno', email: 'paula.moreno@mail.com', patientName: 'Carmen Moreno', beds: ['BED-203-QW77'], relationship: 'Spouse', state: 'Active' }
])

const patientResources = ref([
  { id: 1, patientName: 'Jose Robles', deviceId: 'BED-201-AF12', status: 'Occupied' },
  { id: 2, patientName: 'Elena Ruiz', deviceId: 'BED-114-CD45', status: 'Occupied' },
  { id: 3, patientName: 'Antonio Leon', deviceId: 'BED-317-ZX90', status: 'Available' },
  { id: 4, patientName: 'Carmen Moreno', deviceId: 'BED-203-QW77', status: 'Occupied' }
])

const emptyStaffForm = () => ({ id: null, name: '', email: '', role: staffRoles[0], area: staffAreas[0] })
const emptyFamilyForm = () => ({ id: null, name: '', email: '', patientName: '', relationship: '', state: 'Pending', beds: [] })

const staffForm = ref(emptyStaffForm())
const familyForm = ref(emptyFamilyForm())

const normalizedSearch = computed(() => search.value.trim().toLowerCase())

const matchesSearch = (values) => !normalizedSearch.value || values.some(value =>
  String(value).toLowerCase().includes(normalizedSearch.value)
)

const filteredStaff = computed(() =>
  staffMembers.value.filter(member => matchesSearch([member.name, member.email, member.role, member.area]))
)

const filteredFamilies = computed(() =>
  familyAccounts.value.filter(relative =>
    matchesSearch([relative.name, relative.email, relative.patientName, relative.beds.join(' '), relative.relationship])
  )
)

const filteredResources = computed(() =>
  patientResources.value.filter(resource =>
    matchesSearch([resource.patientName, resource.deviceId, resource.status])
  )
)

const activeFamilies = computed(() => familyAccounts.value.filter(item => item.state === 'Active').length)
const pendingInvites = computed(() => familyAccounts.value.filter(item => item.state === 'Pending').length)
const occupiedResources = computed(() => patientResources.value.filter(item => item.status === 'Occupied').length)

const summaryCards = computed(() => [
  { label: 'Staff', value: staffMembers.value.length, meta: 'Registered users' },
  { label: 'Families', value: activeFamilies.value, meta: `${pendingInvites.value} pending` },
  { label: 'Resources', value: patientResources.value.length, meta: `${occupiedResources.value} occupied` },
  { label: 'Roles', value: 4, meta: 'Global to guest scope' }
])

const openStaffModal = (member = null) => {
  staffForm.value = member ? { ...member } : emptyStaffForm()
  modal.value = { type: 'staff' }
}

const openFamilyModal = (relative = null) => {
  familyForm.value = relative ? { ...relative, beds: [...relative.beds] } : emptyFamilyForm()
  modal.value = { type: 'family' }
}

const closeModal = () => {
  modal.value = { type: '' }
  staffForm.value = emptyStaffForm()
  familyForm.value = emptyFamilyForm()
}

const toggleAssignedBed = (deviceId) => {
  const beds = familyForm.value.beds
  familyForm.value.beds = beds.includes(deviceId) ? beds.filter(id => id !== deviceId) : [...beds, deviceId]
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

const saveFamily = () => {
  if (!familyForm.value.name || !familyForm.value.email) return
  const selectedBeds = familyForm.value.beds
  const primaryResource = patientResources.value.find(item => selectedBeds.includes(item.deviceId))
  const payload = {
    ...familyForm.value,
    beds: [...selectedBeds],
    patientName: familyForm.value.patientName || primaryResource?.patientName || 'Unassigned'
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
  if (modal.value.type === 'family') saveFamily()
}

const removeFamily = (id) => {
  familyAccounts.value = familyAccounts.value.filter(item => item.id !== id)
}
</script>

<style scoped>
.users-page { max-width: 1280px; margin: 0 auto; }
.page-header, .toolbar, .section-head, .item-top, .family-link, .table-head, .table-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.page-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
.page-title { margin: 0; font-size: 1.9rem; font-weight: 800; color: var(--text-main); }
.page-subtitle, .meta { color: var(--text-muted); }
.page-subtitle { margin: 6px 0 0; }
.actions, .tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.summary-grid, .content-grid { display: grid; gap: 16px; }
.summary-grid { grid-template-columns: repeat(4, 1fr); margin-bottom: 1.25rem; }
.content-grid { grid-template-columns: repeat(2, 1fr); }
.panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,.08); padding: 16px; }
.toolbar { margin-bottom: 1.25rem; }
.search { width: 100%; max-width: 420px; box-sizing: border-box; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-main); color: var(--text-main); outline: none; }
.btn, .tab, .link-btn { border-radius: 6px; font-weight: 600; cursor: pointer; transition: .2s ease; }
.btn, .tab { padding: 9px 12px; border: 1px solid var(--border-color); }
.btn-primary, .tab.active { background: #3b82f6; border-color: #3b82f6; color: white; }
.btn-muted, .btn-ghost, .tab { background: var(--bg-main); color: var(--text-main); }
.section-head { margin-bottom: 12px; }
.section-head h3 { margin: 0; color: var(--text-main); font-size: 1.05rem; }
.stack { display: grid; gap: 10px; }
.item-row, .family-card, .table-row { border: 1px solid var(--border-color); background: var(--bg-main); border-radius: 10px; padding: 12px; }
.item-row { display: grid; grid-template-columns: 42px 1fr auto; gap: 12px; align-items: center; }
.family-actions, .tags, .bed-options, .form-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.avatar { width: 42px; height: 42px; border-radius: 10px; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.item-main { min-width: 0; }
.meta { font-size: .84rem; }
.block { display: block; margin-top: 3px; }
.pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 9px; border-radius: 999px; font-size: .75rem; font-weight: 700; }
.pill.ok { background: rgba(16,185,129,.15); color: #10b981; }
.pill.warn { background: rgba(249,115,22,.14); color: #ea580c; }
.pill.muted { background: rgba(100,116,139,.14); color: #64748b; }
.link-btn { border: none; background: transparent; color: #3b82f6; padding: 0; }
.link-btn.danger { color: #ef4444; }
.family-link { margin-top: 10px; flex-wrap: wrap; }
.family-actions { margin-top: 10px; justify-content: flex-end; }
.tag { font-size: .75rem; color: var(--text-main); background: var(--bg-card); padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border-color); }
.table { border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; }
.table-head { padding: 10px 12px; background: var(--bg-main); color: var(--text-muted); font-size: .75rem; text-transform: uppercase; font-weight: 700; }
.table-row { border-top: 1px solid var(--border-color); }
.stat-value { display: block; color: var(--text-main); font-size: 1.7rem; line-height: 1; margin: 8px 0 6px; }
.eyebrow { font-size: .75rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, .45); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 1000; }
.modal { width: min(720px, 100%); }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); margin: 14px 0; }
.field { display: grid; gap: 6px; color: var(--text-main); font-size: .85rem; }
.field-full { grid-column: 1 / -1; }
.bed-option { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-main); }
@media (max-width: 1024px) { .summary-grid, .content-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 820px) {
  .page-header, .toolbar, .item-top, .table-head, .table-row { flex-direction: column; align-items: flex-start; }
  .summary-grid, .content-grid { grid-template-columns: 1fr; }
  .item-row { grid-template-columns: 1fr; }
  .search { max-width: none; }
  .form-grid { grid-template-columns: 1fr; }
  .family-actions { justify-content: flex-start; }
}
</style>
