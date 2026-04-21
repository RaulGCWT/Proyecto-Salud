import { useAuthStore } from '~/stores/auth'
import { PERMISSIONS } from '~/utils/permissions'
import {
  buildFamilyInvitePayload,
  buildFamilyUserPayload,
  buildResidentPayload,
  buildStaffPayload,
  createEmptyFamilyForm,
  createEmptyFamilyUserForm,
  createEmptyResidentForm,
  createEmptyStaffForm,
  mapDevice,
  mapFamilyAccount,
  mapInvitation,
  mapResident,
  mapStaffMember,
  sameId
} from '~/utils/users/usersMappers'

const STAFF_API_BASE = 'http://localhost:3001/MonitoringStaffMembers'
const RESIDENTS_API_BASE = 'http://localhost:3001/MonitoringResidents'
const DEVICES_API_BASE = 'http://localhost:3001/MonitoringDevices'
const FAMILY_USERS_API_BASE = 'http://localhost:3001/MonitoringFamilyUsers'
const INVITES_API_BASE = 'http://localhost:3001/MonitoringInvites'

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

function canAccessCreateActions(auth) {
  return auth.permissions.includes(PERMISSIONS.USER_CREATE_RECORDS)
}

function buildUpdateEndpoint(baseUrl, id) {
  return `${baseUrl}/${id}`
}

export function useUsersManagement() {
  const auth = useAuthStore()
  const search = ref('')
  const activeTab = ref('all')
  const modal = ref({ type: '' })

  const { data: staffData, refresh: refreshStaff } = useFetch(STAFF_API_BASE, {
    server: false,
    default: () => []
  })

  const { data: residentsData, refresh: refreshResidents } = useFetch(RESIDENTS_API_BASE, {
    server: false,
    default: () => []
  })

  const { data: devicesData, pending: resourcesLoading } = useFetch(DEVICES_API_BASE, {
    server: false,
    default: () => []
  })

  const { data: familyUsersData, refresh: refreshFamilyUsers } = useFetch(FAMILY_USERS_API_BASE, {
    server: false,
    default: () => []
  })

  const { data: invitesData, refresh: refreshInvites } = useFetch(INVITES_API_BASE, {
    server: false,
    default: () => []
  })

  const staffMembers = computed(() =>
    (Array.isArray(staffData.value) ? staffData.value : []).map(mapStaffMember)
  )

  const residents = computed(() =>
    (Array.isArray(residentsData.value) ? residentsData.value : []).map(mapResident)
  )

  const devices = computed(() =>
    (Array.isArray(devicesData.value) ? devicesData.value : []).map(mapDevice)
  )

  const familyAccounts = computed(() =>
    (Array.isArray(familyUsersData.value) ? familyUsersData.value : []).map((item, index) =>
      mapFamilyAccount(item, residents.value, index)
    )
  )

  const invitations = computed(() =>
    (Array.isArray(invitesData.value) ? invitesData.value : []).map(mapInvitation)
  )

  const staffForm = ref(createEmptyStaffForm())
  const residentForm = ref(createEmptyResidentForm())
  const familyForm = ref(createEmptyFamilyForm())
  const familyUserForm = ref(createEmptyFamilyUserForm())

  const query = computed(() => search.value.trim().toLowerCase())
  const canCreateRecords = computed(() => canAccessCreateActions(auth))
  const sameUserId = (left, right) => sameId(left, right)

  const findResidentById = (residentId) =>
    residents.value.find(resident => sameUserId(resident.id, residentId))

  const matchesSearch = (values) =>
    !query.value || values.some(value => String(value).toLowerCase().includes(query.value))

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

  const assignedDeviceIds = computed(() =>
    new Set(residents.value.map(resident => resident.deviceId).filter(Boolean))
  )

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
    staffForm.value = createEmptyStaffForm()
    residentForm.value = createEmptyResidentForm()
    familyForm.value = createEmptyFamilyForm()
    familyUserForm.value = createEmptyFamilyUserForm()
  }

  const closeModal = () => {
    modal.value = { type: '' }
    resetForms()
  }

  const openStaffModal = (member = null) => {
    if (!member && !canCreateRecords.value) return
    staffForm.value = member ? { ...createEmptyStaffForm(), ...member } : createEmptyStaffForm()
    modal.value = { type: 'staff' }
  }

  const openResidentModal = (resident = null) => {
    if (!resident && !canCreateRecords.value) return
    residentForm.value = resident ? { ...createEmptyResidentForm(), ...resident } : createEmptyResidentForm()
    modal.value = { type: 'resident' }
  }

  const openFamilyModal = (relative = null) => {
    if (!relative && !canCreateRecords.value) return
    familyForm.value = relative
      ? { ...createEmptyFamilyForm(), ...relative, residentId: relative.residentId || '' }
      : createEmptyFamilyForm()
    modal.value = { type: 'family' }
  }

  const openFamilyModalForResident = (resident) => {
    openFamilyModal()
    familyForm.value.residentId = resident.id
    syncFamilyResidentLink()
  }

  const openFamilyUserModal = (relative) => {
    familyUserForm.value = {
      ...createEmptyFamilyUserForm(),
      ...relative,
      residentId: relative.residentId || '',
      deviceIdOverride: relative.deviceIdOverride || ''
    }
    modal.value = { type: 'family-user' }
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

    return devices.value.filter((device) => {
      if (!isAssignedDevice(device.deviceId)) return true
      return currentResident?.deviceId === device.deviceId
    })
  }

  const saveStaffMember = async () => {
    if (!canCreateRecords.value && !staffForm.value.id) {
      alert('You do not have permission to create staff users.')
      return
    }

    if (!staffForm.value.name || !staffForm.value.email) return

    try {
      const payload = buildStaffPayload(staffForm.value)
      const endpoint = staffForm.value.id
        ? buildUpdateEndpoint(STAFF_API_BASE, staffForm.value.id)
        : STAFF_API_BASE

      await $fetch(endpoint, {
        method: staffForm.value.id ? 'PUT' : 'POST',
        body: payload
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
      const payload = buildResidentPayload(residentForm.value)
      const endpoint = residentForm.value.id
        ? buildUpdateEndpoint(RESIDENTS_API_BASE, residentForm.value.id)
        : RESIDENTS_API_BASE

      await $fetch(endpoint, {
        method: residentForm.value.id ? 'PUT' : 'POST',
        body: payload
      })

      await Promise.all([
        refreshResidents(),
        refreshFamilyUsers(),
        refreshInvites()
      ])
      closeModal()
    } catch (error) {
      console.error('Error saving resident:', error)
      alert('No se pudo guardar el residente.')
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

    const payload = buildFamilyInvitePayload(familyForm.value, resident)

    try {
      const invitation = await $fetch(INVITES_API_BASE, {
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
    const payload = buildFamilyUserPayload(familyUserForm.value, resident)

    try {
      await $fetch(buildUpdateEndpoint(FAMILY_USERS_API_BASE, familyUserForm.value.id), {
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

  const saveModal = async () => {
    if (modal.value.type === 'staff') return saveStaffMember()
    if (modal.value.type === 'resident') return saveResidentRecord()
    if (modal.value.type === 'family') return saveFamilyInvite()
    return saveFamilyUser()
  }

  const toggleFamilyState = async (familyId) => {
    const familyUser = familyAccounts.value.find(relative => sameId(relative.id, familyId))
    if (!familyUser) return

    try {
      await $fetch(buildUpdateEndpoint(FAMILY_USERS_API_BASE, familyUser.id), {
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
      await $fetch(`${INVITES_API_BASE}/${inviteId}/state`, {
        method: 'PUT',
        body: { state }
      })

      await refreshInvites()
    } catch (error) {
      console.error('Error updating invitation state:', error)
      alert('Could not update invitation state.')
    }
  }

  return { auth, search, activeTab, modal, tabs, staffRoles, staffAreas, staffMembers, residents, devices, familyAccounts, invitations, resourcesLoading, staffForm, residentForm, familyForm, familyUserForm, canCreateRecords, summaryCards, modalTitle, filteredStaff, filteredResidents, filteredFamilies, filteredInvitations, filteredDevices, showSection, openStaffModal, openResidentModal, openFamilyModal, openFamilyModalForResident, openFamilyUserModal, closeModal, syncFamilyResidentLink, syncFamilyUserResidentLink, familyCountForResident, isAssignedDevice, availableDeviceOptions, saveModal, toggleFamilyState, formatDate, copyInviteLink, updateInviteState }
}
