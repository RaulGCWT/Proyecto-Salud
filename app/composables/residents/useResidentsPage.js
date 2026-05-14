import { computed, ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useHealthStore } from '~/stores/health'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'

const STATUS_OPTIONS = ['Active', 'Monitoring', 'Pending Setup']

function createEmptyForm() {
  return { id: '', name: '', status: 'Active', deviceId: '', notes: '', assignmentHistory: [] }
}

export function useResidentsPage() {
  const { public: { apiBase } } = useRuntimeConfig()
  const auth = useAuthStore()
  const health = useHealthStore()
  const backendHeaders = computed(() => buildBackendAuthHeaders(auth))

  const { data: residentsRaw, refresh: refreshResidents } = useFetch(`${apiBase}/residents`, {
    server: false,
    headers: backendHeaders.value,
    default: () => []
  })

  const { data: devicesRaw } = useFetch(`${apiBase}/devices`, {
    server: false,
    headers: backendHeaders.value,
    default: () => []
  })

  const modal = ref({ open: false, mode: '' })
  const form = ref(createEmptyForm())
  const isSaving = ref(false)
  const searchQuery = ref('')

  const residents = computed(() => {
    const raw = Array.isArray(residentsRaw.value) ? residentsRaw.value : []
    return raw.map(r => ({
      id: String(r.id || r.residentId || '').trim(),
      name: String(r.name || '').trim(),
      status: String(r.status || 'Active').trim(),
      deviceId: String(r.deviceId || '').trim(),
      notes: String(r.notes || '').trim(),
      ownerId: String(r.ownerId || '').trim(),
      assignmentHistory: Array.isArray(r.assignmentHistory) ? r.assignmentHistory : []
    }))
  })

  const deviceOptions = computed(() => {
    const raw = Array.isArray(devicesRaw.value) ? devicesRaw.value : []
    return [
      { value: '', label: 'Unassigned' },
      ...raw.map(d => ({
        value: String(d.mac || d.deviceId || d.id || '').trim(),
        label: String(d.name || d.deviceId || d.mac || 'Unknown').trim()
      })).filter(d => d.value)
    ]
  })

  const filteredResidents = computed(() => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return residents.value
    return residents.value.filter(r =>
      r.name.toLowerCase().includes(q) ||
      r.status.toLowerCase().includes(q) ||
      r.deviceId.toLowerCase().includes(q) ||
      r.notes.toLowerCase().includes(q)
    )
  })

  const summaryCards = computed(() => {
    const total = residents.value.length
    const assigned = residents.value.filter(r => r.deviceId).length
    return [
      { label: 'Total', value: String(total), note: 'Registered residents' },
      { label: 'Assigned', value: String(assigned), note: 'With a bed assigned' },
      { label: 'Unassigned', value: String(total - assigned), note: 'Without a bed' }
    ]
  })

  const openCreateModal = () => {
    form.value = createEmptyForm()
    modal.value = { open: true, mode: 'create' }
  }

  const openEditModal = (resident) => {
    form.value = {
      ...createEmptyForm(),
      ...resident,
      assignmentHistory: Array.isArray(resident.assignmentHistory) ? resident.assignmentHistory : []
    }
    modal.value = { open: true, mode: 'edit' }
  }

  const formatHistoryDate = (value) => {
    if (!value) return '—'
    const d = new Date(value)
    return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    })
  }

  const closeModal = () => {
    modal.value = { open: false, mode: '' }
  }

  const saveResident = async () => {
    const name = form.value.name.trim()
    if (!name) {
      health.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Resident name is required.' }
      return
    }

    isSaving.value = true
    try {
      const isEdit = Boolean(form.value.id)
      const endpoint = isEdit
        ? `${apiBase}/residents/${form.value.id}`
        : `${apiBase}/residents`

      await $fetch(endpoint, {
        method: isEdit ? 'PUT' : 'POST',
        headers: backendHeaders.value,
        body: {
          name,
          status: form.value.status || 'Active',
          deviceId: form.value.deviceId || '',
          notes: form.value.notes || ''
        }
      })

      await refreshResidents()
      health.lastToast = {
        id: Date.now(),
        sensor: 'SYSTEM',
        message: isEdit ? 'Resident updated successfully.' : 'Resident created successfully.'
      }
      closeModal()
    } catch {
      health.lastToast = { id: Date.now(), sensor: 'SYSTEM', message: 'Could not save resident.' }
    } finally {
      isSaving.value = false
    }
  }

  return {
    residents,
    filteredResidents,
    deviceOptions,
    summaryCards,
    searchQuery,
    modal,
    form,
    isSaving,
    statusOptions: STATUS_OPTIONS,
    openCreateModal,
    openEditModal,
    closeModal,
    saveResident,
    formatHistoryDate
  }
}
