<template>
  <div class="rules-page">
    <section class="rules-shell">
      <header class="page-header">
        <div class="page-heading">
          <p class="page-eyebrow">Rules Library</p>
          <h1 class="page-title">Monitoring Rules</h1>
          <p class="page-subtitle">
            Define the thresholds that turn biometric measurements into clinical alerts.
          </p>
        </div>

        <div class="page-actions">
          <button class="action-button action-button--primary" type="button" @click="openCreateModal">
            <span class="material-symbols-outlined" aria-hidden="true">add</span>
            <span>Add Rule</span>
          </button>
        </div>
      </header>

      <section class="summary-grid">
        <article v-for="card in summaryCards" :key="card.label" class="summary-card">
          <div class="summary-card__top">
            <div :class="['summary-icon', card.tone]">
              <span class="material-symbols-outlined" aria-hidden="true">{{ card.icon }}</span>
            </div>
            <span class="summary-label">{{ card.label }}</span>
          </div>
          <strong class="summary-value">{{ card.value }}</strong>
          <p class="summary-note">{{ card.note }}</p>
        </article>
      </section>

      <section class="toolbar">
        <label class="search-field">
          <span class="material-symbols-outlined search-field__icon" aria-hidden="true">search</span>
          <input
            v-model.trim="searchQuery"
            class="search-input"
            type="text"
            placeholder="Search by name, variable or value..."
            autocomplete="off"
          />
        </label>

        <div class="toolbar-filters" aria-label="Assignment filters">
          <button
            v-for="option in assignmentFilterOptions"
            :key="option.value"
            type="button"
            class="filter-pill"
            :class="{ 'filter-pill--active': assignmentFilter === option.value }"
            @click="assignmentFilter = option.value"
          >
            {{ option.label }}
          </button>
        </div>

        <div class="toolbar-meta">
          <span class="toolbar-meta__label">Visible</span>
          <span class="toolbar-meta__value">{{ visibleRules.length }} / {{ totalRules }}</span>
        </div>
      </section>

      <section class="rules-grid">
        <article v-for="rule in visibleRules" :key="rule.id" class="rule-card">
          <div class="rule-card__header">
            <div>
              <p class="rule-card__eyebrow">{{ variableLabel(rule.variable) }}</p>
              <h2 class="rule-card__title">{{ rule.name }}</h2>
            </div>
            <span class="rule-badge">{{ operatorLabel(rule.operator) }}</span>
          </div>

          <div class="rule-equation">
            <span class="equation-chip">{{ variableShortLabel(rule.variable) }}</span>
            <span class="equation-symbol">{{ rule.operator }}</span>
            <span class="equation-value">{{ formatRuleValue(rule.value) }}</span>
          </div>

          <div v-if="assignmentDisplayLabel(rule)" class="rule-assignment">
            <div class="rule-assignment__top">
              <span class="rule-assignment__label">Assigned to</span>
              <span :class="['rule-assignment__chip', `rule-assignment__chip--${rule.assignedToType}`]">
                {{ assignmentTypeLabel(rule.assignedToType) }}
              </span>
            </div>
            <span class="rule-assignment__value">{{ assignmentTargetLabel(rule.assignedToId) }}</span>
          </div>

          <footer class="rule-card__footer">
            <div class="rule-actions">
              <button class="icon-button icon-button--edit" type="button" @click="openEditModal(rule)">
                <span class="material-symbols-outlined" aria-hidden="true">edit</span>
              </button>
              <button class="icon-button icon-button--danger" type="button" @click="rulesStore.deleteRule(rule.id)">
                <span class="material-symbols-outlined" aria-hidden="true">delete_outline</span>
              </button>
            </div>
          </footer>
        </article>

      </section>

      <section v-if="!visibleRules.length" class="empty-state">
        <div class="empty-state__icon">
          <span class="material-symbols-outlined" aria-hidden="true">rule</span>
        </div>
        <h2>No rules found</h2>
        <p v-if="searchQuery">
          Try changing the search term or create a new rule to start monitoring this scope.
        </p>
        <p v-else-if="assignmentFilter !== 'all'">
          No rules match the {{ assignmentFilterLabel.toLowerCase() }} assignment filter. Try switching back to All.
        </p>
        <p v-else>No active rules are available in this scope yet.</p>
        <button class="empty-state__action" type="button" @click="openCreateModal">
          Create first rule
        </button>
      </section>
    </section>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card" role="dialog" aria-modal="true" :aria-label="isEditing ? 'Edit rule' : 'Create rule'">
        <header class="modal-card__header">
          <div>
            <p class="modal-card__eyebrow">{{ isEditing ? 'Edit rule' : 'Create rule' }}</p>
            <h3 class="modal-card__title">{{ isEditing ? 'Update monitoring logic' : 'Define monitoring logic' }}</h3>
          </div>
          <button class="modal-close" type="button" @click="closeModal">
            <span class="material-symbols-outlined" aria-hidden="true">close</span>
          </button>
        </header>

        <form class="modal-form" @submit.prevent="saveRule">
          <div class="form-group">
            <label class="form-label" for="rule-name">Rule name</label>
            <input
              id="rule-name"
              v-model.trim="currentRule.name"
              class="form-input"
              type="text"
              placeholder="e.g. Critical Heart Rate"
              autocomplete="off"
              required
            />
          </div>

          <div class="modal-grid">
            <div class="form-group">
              <label class="form-label">Variable</label>
              <div class="rule-dropdown" @click.stop>
                <button
                  class="form-input form-input--select"
                  type="button"
                  :aria-expanded="activeRuleDropdown === 'variable' ? 'true' : 'false'"
                  @click="toggleRuleDropdown('variable')"
                >
                  <span>{{ variableLabel(currentRule.variable) }}</span>
                  <span class="material-symbols-outlined form-input__icon" aria-hidden="true">expand_more</span>
                </button>

                <div v-if="activeRuleDropdown === 'variable'" class="dropdown-menu">
                  <button
                    v-for="option in variableOptions"
                    :key="option.value"
                    class="dropdown-item"
                    :class="{ 'dropdown-item--active': currentRule.variable === option.value }"
                    type="button"
                    @click="selectVariable(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Operator</label>
              <div class="rule-dropdown" @click.stop>
                <button
                  class="form-input form-input--select"
                  type="button"
                  :aria-expanded="activeRuleDropdown === 'operator' ? 'true' : 'false'"
                  @click="toggleRuleDropdown('operator')"
                >
                  <span>{{ operatorLabel(currentRule.operator) }}</span>
                  <span class="material-symbols-outlined form-input__icon" aria-hidden="true">expand_more</span>
                </button>

                <div v-if="activeRuleDropdown === 'operator'" class="dropdown-menu">
                  <button
                    v-for="option in operatorOptions"
                    :key="option.value"
                    class="dropdown-item"
                    :class="{ 'dropdown-item--active': currentRule.operator === option.value }"
                    type="button"
                    @click="selectOperator(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="canAssignRules" class="modal-grid">
            <div class="form-group">
              <label class="form-label">Assign to</label>
              <div class="rule-dropdown" @click.stop>
                <button
                  class="form-input form-input--select"
                  type="button"
                  :aria-expanded="activeRuleDropdown === 'assignment-type' ? 'true' : 'false'"
                  @click="toggleRuleDropdown('assignment-type')"
                >
                  <span>{{ assignmentTypeLabel(currentRule.assignedToType) }}</span>
                  <span class="material-symbols-outlined form-input__icon" aria-hidden="true">expand_more</span>
                </button>

                <div v-if="activeRuleDropdown === 'assignment-type'" class="dropdown-menu">
                  <button
                    v-for="option in assignmentTypeOptions"
                    :key="option.value"
                    class="dropdown-item"
                    :class="{ 'dropdown-item--active': currentRule.assignedToType === option.value }"
                    type="button"
                    @click="selectAssignmentType(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>

            <div v-if="currentRule.assignedToType !== 'none'" class="form-group">
              <label class="form-label">Target</label>
              <div class="rule-dropdown" @click.stop>
                <button
                  class="form-input form-input--select"
                  type="button"
                  :aria-expanded="activeRuleDropdown === 'assignment-target' ? 'true' : 'false'"
                  @click="toggleRuleDropdown('assignment-target')"
                >
                  <span>{{ assignmentTargetLabel(currentRule.assignedToId) }}</span>
                  <span class="material-symbols-outlined form-input__icon" aria-hidden="true">expand_more</span>
                </button>

                <div v-if="activeRuleDropdown === 'assignment-target'" class="dropdown-menu">
                  <button
                    v-for="option in assignmentTargetOptions"
                    :key="option.value"
                    class="dropdown-item"
                    :class="{ 'dropdown-item--active': currentRule.assignedToId === option.value }"
                    type="button"
                    @click="selectAssignmentTarget(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="rule-value">Threshold value</label>
            <input
              id="rule-value"
              v-model.number="currentRule.value"
              class="form-input"
              type="number"
              min="0"
              step="1"
              inputmode="numeric"
              required
            />
          </div>

          <div class="modal-preview">
            <span class="modal-preview__label">Preview</span>
            <div class="modal-preview__equation">
              <span>{{ variableLabel(currentRule.variable) }}</span>
              <span>{{ currentRule.operator }}</span>
              <span>{{ formatRuleValue(currentRule.value) }}</span>
            </div>
          </div>

          <footer class="modal-actions">
            <button class="action-button action-button--ghost" type="button" @click="closeModal">
              Cancel
            </button>
            <button class="action-button action-button--primary" type="submit">
              {{ isEditing ? 'Save changes' : 'Create rule' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRulesStore } from '~/stores/rules'
import { useAuthStore } from '~/stores/auth'
import { canAssignRules as canAssignRulesForUser } from '~/utils/accessContext'

useHead({
  title: 'Monitoring Rules | Clinical Sentinel'
})

const rulesStore = useRulesStore()
const auth = useAuthStore()

const STAFF_API_BASE = 'http://localhost:3001/MonitoringStaffMembers'
const RESIDENTS_API_BASE = 'http://localhost:3001/MonitoringResidents'
const DEVICES_API_BASE = 'http://localhost:3001/MonitoringDevices'
const FAMILY_USERS_API_BASE = 'http://localhost:3001/MonitoringFamilyUsers'

const searchQuery = ref('')
const assignmentFilter = ref('all')
const isModalOpen = ref(false)
const isEditing = ref(false)
const currentRuleId = ref(null)
const activeRuleDropdown = ref('')
const currentRule = ref(createEmptyRule())
const { data: staffData } = useFetch(STAFF_API_BASE, { server: false, default: () => [] })
const { data: residentsData } = useFetch(RESIDENTS_API_BASE, { server: false, default: () => [] })
const { data: devicesData } = useFetch(DEVICES_API_BASE, { server: false, default: () => [] })
const { data: familyUsersData } = useFetch(FAMILY_USERS_API_BASE, { server: false, default: () => [] })

const variableOptions = [
  { value: 'hr', label: 'Heart Rate' },
  { value: 'hrv', label: 'HRV' },
  { value: 'resp', label: 'Respiratory Rate' }
]

const operatorOptions = [
  { value: '>', label: 'Greater than' },
  { value: '<', label: 'Less than' },
  { value: '=', label: 'Equal to' }
]

const assignmentTypeOptions = [
  { value: 'none', label: 'None' },
  { value: 'device', label: 'Device' },
  { value: 'user', label: 'User' }
]

const assignmentFilterOptions = [
  { value: 'all', label: 'All' },
  { value: 'device', label: 'Device' },
  { value: 'user', label: 'User' },
  { value: 'none', label: 'Unassigned' }
]

const assignmentFilterLabel = computed(() => {
  return assignmentFilterOptions.find(option => option.value === assignmentFilter.value)?.label || 'All'
})

const canAssignRules = computed(() => canAssignRulesForUser(auth.user || {}))

const deviceAssignmentOptions = computed(() => {
  const devices = Array.isArray(devicesData.value) ? devicesData.value : []

  return devices
    .map((device) => {
      const mac = String(device.mac || '').trim()
      const deviceId = String(device.deviceId || '').trim()
      const fallbackId = String(device.id || '').trim()
      const value = mac || deviceId || fallbackId
      if (!value) return null

      return {
        value,
        label: device.patientName || device.name || value,
        aliases: [mac, deviceId, fallbackId].filter(Boolean)
      }
    })
    .filter(Boolean)
})

const userAssignmentOptions = computed(() => {
  const staffMembers = Array.isArray(staffData.value) ? staffData.value : []
  const residents = Array.isArray(residentsData.value) ? residentsData.value : []
  const familyUsers = Array.isArray(familyUsersData.value) ? familyUsersData.value : []

  return [
    ...staffMembers.map((item) => {
      const id = String(item.email || item.id || '').trim()
      if (!id) return null

      return {
        value: id,
        label: `${item.name || id} · Staff`,
        aliases: [item.id, item.email].filter(Boolean).map(value => String(value).trim())
      }
    }),
    ...residents.map((item) => {
      const id = String(item.residentId || item.id || '').trim()
      if (!id) return null

      return {
        value: id,
        label: `${item.name || id} · Resident`,
        aliases: [item.id, item.residentId].filter(Boolean).map(value => String(value).trim())
      }
    }),
    ...familyUsers.map((item) => {
      const id = String(item.email || item.id || '').trim()
      if (!id) return null

      return {
        value: id,
        label: `${item.name || id} · Family`,
        aliases: [item.id, item.email].filter(Boolean).map(value => String(value).trim())
      }
    })
  ].filter(Boolean)
})
const assignmentTargetOptions = computed(() => {
  if (currentRule.value.assignedToType === 'device') return deviceAssignmentOptions.value
  if (currentRule.value.assignedToType === 'user') return userAssignmentOptions.value
  return []
})

const summaryCards = computed(() => {
  const rules = rulesStore.rules
  return [
    {
      label: 'Total rules',
      value: rules.length.toLocaleString(),
      note: 'Thresholds currently loaded in this scope.',
      icon: 'rule',
      tone: 'summary-icon--blue'
    },
    {
      label: 'Heart rate',
      value: rules.filter(rule => normalizeVariable(rule.variable) === 'hr').length.toLocaleString(),
      note: 'Rules linked to cardiac monitoring.',
      icon: 'favorite',
      tone: 'summary-icon--red'
    },
    {
      label: 'HRV',
      value: rules.filter(rule => normalizeVariable(rule.variable) === 'hrv').length.toLocaleString(),
      note: 'Rules tracking variability changes.',
      icon: 'monitor_heart',
      tone: 'summary-icon--teal'
    },
    {
      label: 'Respiratory',
      value: rules.filter(rule => normalizeVariable(rule.variable) === 'resp').length.toLocaleString(),
      note: 'Rules for respiratory rate thresholds.',
      icon: 'air',
      tone: 'summary-icon--amber'
    }
  ]
})

const totalRules = computed(() => rulesStore.rules.length)

const visibleRules = computed(() => {
  const query = normalizeSearchValue(searchQuery.value)
  return rulesStore.rules.filter((rule) => {
    if (assignmentFilter.value !== 'all') {
      const ruleAssignmentType = String(rule.assignedToType || 'none').trim()
      if (assignmentFilter.value === 'none') {
        if (ruleAssignmentType !== 'none') return false
      } else if (ruleAssignmentType !== assignmentFilter.value) {
        return false
      }
    }

    if (!query) return true

    const searchableValues = [
      rule.name,
      rule.variable,
      operatorLabel(rule.operator),
      formatRuleValue(rule.value),
      assignmentDisplayLabel(rule),
      assignmentTypeLabel(rule.assignedToType),
      assignmentTargetLabel(rule.assignedToId)
    ]
      .filter(Boolean)
      .map(value => normalizeSearchValue(value))

    return searchableValues.some(value => value.includes(query))
  })
})

onMounted(() => {
  rulesStore.fetchRules()
  document.addEventListener('click', closeRuleDropdowns)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeRuleDropdowns)
  document.removeEventListener('keydown', handleKeydown)
})

function createEmptyRule() {
  return {
    name: '',
    variable: 'hr',
    operator: '>',
    value: 80,
    assignedToType: 'none',
    assignedToId: ''
  }
}

function normalizeVariable(value) {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'heartrate' || normalized === 'heart_rate') return 'hr'
  if (normalized === 'respiratoryrate' || normalized === 'resp_rate' || normalized === 'respiratory_rate') return 'resp'
  return normalized
}

function normalizeSearchValue(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '')
}

function variableLabel(value) {
  const normalized = normalizeVariable(value)
  return variableOptions.find(option => option.value === normalized)?.label || 'Unknown variable'
}

function variableShortLabel(value) {
  const normalized = normalizeVariable(value)
  if (normalized === 'hr') return 'HR'
  if (normalized === 'hrv') return 'HRV'
  if (normalized === 'resp') return 'RESP'
  return 'RULE'
}

function operatorLabel(value) {
  return operatorOptions.find(option => option.value === String(value || '').trim())?.label || 'Threshold'
}

function assignmentTypeLabel(value) {
  return assignmentTypeOptions.find(option => option.value === String(value || 'none').trim())?.label || 'None'
}

function normalizeAssignmentTargetId(value) {
  const normalized = String(value || '').trim()
  if (!normalized) return ''
  const knownPrefixes = ['device:', 'user:', 'staff:', 'resident:', 'family:']
  const matchedPrefix = knownPrefixes.find(prefix => normalized.toLowerCase().startsWith(prefix))
  return matchedPrefix ? normalized.slice(matchedPrefix.length) : normalized
}

function assignmentTargetLabel(value, type = currentRule.value.assignedToType) {
  const normalized = resolveAssignmentTargetValue(value, type)
  if (!normalized) return 'Select target'

  const allOptions = String(type || '').trim() === 'device'
    ? deviceAssignmentOptions.value
    : String(type || '').trim() === 'user'
      ? userAssignmentOptions.value
      : [...deviceAssignmentOptions.value, ...userAssignmentOptions.value]
  return allOptions.find(option => option.value === normalized)?.label || normalized
}

function resolveAssignmentTargetValue(value, type = currentRule.value.assignedToType) {
  const normalized = normalizeAssignmentTargetId(value)
  if (!normalized) return ''

  const targetOptions = String(type || '').trim() === 'device'
    ? deviceAssignmentOptions.value
    : String(type || '').trim() === 'user'
      ? userAssignmentOptions.value
      : [...deviceAssignmentOptions.value, ...userAssignmentOptions.value]

  const matchedOption = targetOptions.find((option) => {
    const aliases = Array.isArray(option.aliases) ? option.aliases : []
    return option.value === normalized || aliases.includes(normalized)
  })

  return matchedOption?.value || normalized
}

function assignmentDisplayLabel(rule) {
  const type = String(rule.assignedToType || 'none').trim()
  const id = String(rule.assignedToId || '').trim()

  if (type === 'none' || !id) return ''

  return `${assignmentTypeLabel(type)} · ${assignmentTargetLabel(id, type)}`
}

function formatRuleValue(value) {
  const numericValue = Number(value)
  if (Number.isNaN(numericValue)) return String(value || '0')
  return Number.isInteger(numericValue) ? String(numericValue) : numericValue.toFixed(1)
}

function openCreateModal() {
  isEditing.value = false
  currentRuleId.value = null
  currentRule.value = createEmptyRule()
  activeRuleDropdown.value = ''
  isModalOpen.value = true
}

function openEditModal(rule) {
  isEditing.value = true
  currentRuleId.value = rule.id
  currentRule.value = {
    name: String(rule.name || ''),
    variable: normalizeVariable(rule.variable) || 'hr',
    operator: String(rule.operator || '>'),
    value: Number(rule.value) || 0,
    assignedToType: String(rule.assignedToType || 'none').trim() || 'none',
    assignedToId: resolveAssignmentTargetValue(rule.assignedToId, String(rule.assignedToType || 'none').trim() || 'none')
  }
  activeRuleDropdown.value = ''
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
  currentRuleId.value = null
  activeRuleDropdown.value = ''
}

function toggleRuleDropdown(field) {
  activeRuleDropdown.value = activeRuleDropdown.value === field ? '' : field
}

function closeRuleDropdowns(event) {
  if (event?.target?.closest?.('.rule-dropdown')) return
  activeRuleDropdown.value = ''
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    activeRuleDropdown.value = ''
  }
}

function selectVariable(value) {
  currentRule.value.variable = value
  activeRuleDropdown.value = ''
}

function selectOperator(value) {
  currentRule.value.operator = value
  activeRuleDropdown.value = ''
}

function selectAssignmentType(value) {
  currentRule.value.assignedToType = value
  currentRule.value.assignedToId = ''
  activeRuleDropdown.value = ''
}

function selectAssignmentTarget(value) {
  currentRule.value.assignedToId = resolveAssignmentTargetValue(value, currentRule.value.assignedToType)
  activeRuleDropdown.value = ''
}

async function saveRule() {
  const name = String(currentRule.value.name || '').trim()
  if (!name) return

  const assignedToType = canAssignRules.value ? String(currentRule.value.assignedToType || 'none').trim() : 'none'
  const assignedToId = canAssignRules.value && assignedToType !== 'none'
    ? resolveAssignmentTargetValue(currentRule.value.assignedToId, assignedToType)
    : ''

  const payload = {
    name,
    variable: normalizeVariable(currentRule.value.variable) || 'hr',
    operator: String(currentRule.value.operator || '>').trim(),
    value: Number(currentRule.value.value) || 0,
    assignedToType,
    assignedToId
  }

  if (isEditing.value && currentRuleId.value) {
    await rulesStore.updateRule(currentRuleId.value, payload)
  } else {
    await rulesStore.addRule(payload)
  }

  closeModal()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.rules-page { min-height: 100%; }
.rules-shell { display: flex; flex-direction: column; gap: 22px; max-width: 1440px; margin: 0 auto; padding-bottom: 12px; }
.page-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.page-eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.68rem; font-weight: 900; color: #2559bd; }
.page-title { margin: 0; font-size: clamp(2rem, 3vw, 2.8rem); font-weight: 900; letter-spacing: -0.05em; color: var(--text-main); }
.page-subtitle { margin: 8px 0 0; font-size: 0.95rem; line-height: 1.6; color: var(--text-muted); max-width: 640px; }
.page-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.action-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 16px; border-radius: 16px; border: 1px solid transparent; font-weight: 900; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease, background 0.2s ease; text-decoration: none; }
.action-button:hover { transform: translateY(-1px); }
.action-button--primary { background: linear-gradient(135deg, #00327d 0%, #0047ab 100%); color: #ffffff; box-shadow: 0 14px 30px rgba(37, 89, 189, 0.18); }
.action-button--ghost { background: rgba(255, 255, 255, 0.88); color: var(--text-main); border-color: rgba(148, 163, 184, 0.18); box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04); }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.summary-card { padding: 22px; border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.14); background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94)); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04); }
.summary-card__top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.summary-icon { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; }
.summary-icon span { font-size: 1.2rem; }
.summary-icon--blue { color: #2559bd; background: rgba(37, 89, 189, 0.1); }
.summary-icon--red { color: #b91c1c; background: rgba(239, 68, 68, 0.12); }
.summary-icon--teal { color: #047857; background: rgba(16, 185, 129, 0.1); }
.summary-icon--amber { color: #b45309; background: rgba(245, 158, 11, 0.12); }
.summary-label { font-size: 0.68rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.summary-value { display: block; margin: 0; font-size: clamp(1.9rem, 3vw, 2.7rem); font-weight: 900; letter-spacing: -0.05em; color: var(--text-main); line-height: 1; }
.summary-note { margin: 8px 0 0; color: var(--text-muted); font-size: 0.92rem; line-height: 1.5; }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding: 14px; border-radius: 22px; border: 1px solid var(--border-color); background: rgba(255, 255, 255, 0.84); box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04); }
.search-field { position: relative; flex: 1 1 320px; min-width: 260px; }
.search-field__icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: rgba(100, 116, 139, 0.7); font-size: 1.1rem; }
.search-input { width: 100%; padding: 13px 16px 13px 46px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.2); background: var(--bg-main); color: var(--text-main); font-weight: 700; box-sizing: border-box; outline: none; }
.search-input::placeholder { color: var(--text-muted); }
.toolbar-filters { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.filter-pill { padding: 11px 14px; border-radius: 999px; border: 1px solid rgba(148, 163, 184, 0.18); background: rgba(248, 250, 252, 0.92); color: #475569; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; cursor: pointer; transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease; }
.filter-pill:hover { transform: translateY(-1px); }
.filter-pill--active { color: #2559bd; background: rgba(37, 89, 189, 0.1); border-color: rgba(37, 89, 189, 0.18); box-shadow: 0 10px 18px rgba(37, 89, 189, 0.08); }
.toolbar-meta { padding: 11px 14px; border-radius: 14px; background: rgba(248, 250, 252, 0.96); color: #475569; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; }
.toolbar-meta__label { color: #64748b; margin-right: 6px; }
.rules-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; align-items: start; }
.rule-card { align-self: start; min-height: 0; padding: 22px; border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.14); background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94)); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.04); text-align: left; }
.rule-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 14px; }
.rule-card__eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.68rem; font-weight: 900; color: #2559bd; }
.rule-card__title { margin: 0; font-size: 1.2rem; line-height: 1.35; font-weight: 900; letter-spacing: -0.03em; color: var(--text-main); }
.rule-badge { display: inline-flex; align-items: center; justify-content: center; padding: 7px 10px; border-radius: 999px; font-size: 0.68rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; color: #2559bd; background: rgba(37, 89, 189, 0.08); border: 1px solid rgba(37, 89, 189, 0.14); }
.rule-equation { display: flex; align-items: center; gap: 10px; padding: 14px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.12); background: rgba(248, 250, 252, 0.9); }
.equation-chip { padding: 8px 10px; border-radius: 999px; background: rgba(37, 89, 189, 0.08); color: #2559bd; font-size: 0.66rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; }
.equation-symbol { color: #64748b; font-weight: 900; }
.equation-value { color: var(--text-main); font-weight: 900; }
.rule-assignment { display: flex; flex-direction: column; gap: 8px; margin-top: 14px; padding: 12px 14px; border-radius: 18px; border: 1px solid rgba(37, 89, 189, 0.12); background: rgba(37, 89, 189, 0.05); }
.rule-assignment__top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.rule-assignment__label { font-size: 0.64rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.rule-assignment__chip { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; font-size: 0.62rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; border: 1px solid transparent; }
.rule-assignment__chip--device { background: rgba(37, 89, 189, 0.12); color: #2559bd; border-color: rgba(37, 89, 189, 0.14); }
.rule-assignment__chip--user { background: rgba(16, 185, 129, 0.12); color: #047857; border-color: rgba(16, 185, 129, 0.14); }
.rule-assignment__chip--none { background: rgba(100, 116, 139, 0.12); color: #475569; border-color: rgba(100, 116, 139, 0.14); }
.rule-assignment__value { font-size: 0.8rem; font-weight: 900; color: var(--text-main); line-height: 1.4; }
.rule-card__footer { display: flex; align-items: center; justify-content: flex-end; gap: 14px; margin-top: 18px; padding-top: 16px; border-top: 1px solid rgba(148, 163, 184, 0.12); }
.rule-actions { display: inline-flex; align-items: center; gap: 8px; margin-left: auto; }
.icon-button { width: 40px; height: 40px; display: inline-flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(255, 255, 255, 0.9); color: #475569; cursor: pointer; transition: color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; }
.icon-button:hover { transform: translateY(-1px); }
.icon-button--edit:hover { color: #2559bd; border-color: rgba(37, 89, 189, 0.24); box-shadow: 0 10px 18px rgba(37, 89, 189, 0.08); }
.icon-button--danger:hover { color: #dc2626; border-color: rgba(239, 68, 68, 0.24); box-shadow: 0 10px 18px rgba(239, 68, 68, 0.08); }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 72px 24px; text-align: center; margin-top: 4px; border-radius: 24px; border: 1px dashed rgba(148, 163, 184, 0.22); background: rgba(255, 255, 255, 0.64); }
.empty-state__icon { width: 80px; height: 80px; border-radius: 999px; display: grid; place-items: center; background: rgba(248, 250, 252, 0.98); color: rgba(100, 116, 139, 0.65); margin-bottom: 18px; }
.empty-state__icon .material-symbols-outlined { font-size: 2.4rem; }
.empty-state h2 { margin: 0; font-size: 1.2rem; font-weight: 900; color: var(--text-main); }
.empty-state p { margin: 8px 0 0; max-width: 420px; color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }
.empty-state__action { margin-top: 22px; padding: 12px 16px; border: 1px solid rgba(37, 89, 189, 0.12); border-radius: 14px; background: rgba(37, 89, 189, 0.08); color: #2559bd; font-weight: 900; cursor: pointer; }
.modal-overlay { position: fixed; inset: 0; z-index: 60; display: flex; align-items: center; justify-content: center; padding: 24px; background: rgba(15, 23, 42, 0.34); backdrop-filter: blur(12px); }
.modal-card { width: min(620px, 100%); max-height: min(92vh, 900px); border-radius: 28px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(255, 255, 255, 0.98); box-shadow: 0 28px 60px rgba(15, 23, 42, 0.18); overflow: hidden; display: flex; flex-direction: column; }
.modal-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 24px 24px 20px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); }
.modal-card__eyebrow { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.68rem; font-weight: 900; color: #2559bd; }
.modal-card__title { margin: 0; font-size: 1.4rem; font-weight: 900; letter-spacing: -0.04em; color: var(--text-main); }
.modal-close { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(248, 250, 252, 0.9); color: #475569; cursor: pointer; }
.modal-form { padding: 24px; display: flex; flex-direction: column; gap: 18px; overflow-y: auto; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 0.68rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.form-input { width: 100%; padding: 13px 16px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.2); background: var(--bg-main); color: var(--text-main); font-weight: 700; box-sizing: border-box; outline: none; }
.form-input:focus { border-color: rgba(37, 89, 189, 0.34); box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.08); }
.form-input--select { display: inline-flex; align-items: center; justify-content: space-between; gap: 10px; text-align: left; cursor: pointer; }
.form-input__icon { font-size: 1.05rem; color: #64748b; }
.rule-dropdown { position: relative; }
.dropdown-menu { position: absolute; top: calc(100% + 8px); left: 0; z-index: 20; width: 100%; padding: 8px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(255, 255, 255, 0.98); box-shadow: 0 22px 44px rgba(15, 23, 42, 0.14); max-height: 260px; overflow: auto; }
.dropdown-item { width: 100%; padding: 11px 12px; border: 0; border-radius: 12px; background: transparent; color: var(--text-main); font-size: 0.82rem; font-weight: 800; cursor: pointer; text-align: left; transition: background 0.2s ease, color 0.2s ease; }
.dropdown-item:hover { background: rgba(37, 89, 189, 0.08); color: #2559bd; }
.dropdown-item--active { background: rgba(37, 89, 189, 0.1); color: #2559bd; }
.modal-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.modal-preview { display: flex; flex-direction: column; gap: 10px; padding: 16px; border-radius: 20px; border: 1px solid rgba(148, 163, 184, 0.12); background: rgba(248, 250, 252, 0.9); }
.modal-preview__label { font-size: 0.68rem; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; }
.modal-preview__equation { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; font-weight: 900; color: var(--text-main); }
.modal-actions { display: flex; align-items: center; justify-content: flex-end; gap: 12px; padding-top: 4px; }
.material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; vertical-align: middle; }
@media (max-width: 1100px) { .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .rules-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 900px) { .page-header { align-items: flex-start; } .page-actions { width: 100%; justify-content: flex-start; } }
@media (max-width: 768px) {
  .summary-grid,
  .rules-grid,
  .modal-grid { grid-template-columns: 1fr; }
  .toolbar { padding: 12px; }
  .modal-card__header,
  .modal-form { padding-left: 18px; padding-right: 18px; }
  .rule-card__footer { flex-direction: column; align-items: flex-start; }
  .modal-actions { flex-direction: column-reverse; }
  .modal-actions .action-button { width: 100%; }
  .toolbar-filters { width: 100%; }
  .filter-pill { flex: 1 1 auto; }
  .dropdown-menu { width: 100%; }
}
</style>
