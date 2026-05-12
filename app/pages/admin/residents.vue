<template>
  <div class="residents-page">
    <section class="residents-shell">

      <UiPageHeader
        eyebrow="Resident Directory"
        title="Residents"
        subtitle="Manage residents and their bed assignments."
        back-to="/admin"
      >
        <template #actions>
          <button class="action-button action-button--primary" type="button" @click="openCreateModal">
            <span class="material-symbols-outlined" aria-hidden="true">person_add</span>
            <span>New Resident</span>
          </button>
        </template>
      </UiPageHeader>

      <section class="summary-grid">
        <UiSummaryCard
          v-for="card in summaryCards"
          :key="card.label"
          :label="card.label"
          :value="card.value"
          :note="card.note"
        />
      </section>

      <div class="filters-bar">
        <UiSearchInput v-model="searchQuery" placeholder="Search by name, status or bed..." />
      </div>

      <section class="panel-card">
        <div class="panel-card-header">
          <div>
            <p class="panel-card-eyebrow">Residents</p>
            <h3 class="panel-card-title">Resident Directory</h3>
            <p class="panel-card-subtitle">{{ filteredResidents.length }} residents</p>
          </div>
        </div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Assigned Bed</th>
                <th>Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!filteredResidents.length" class="data-table__empty">
                <td colspan="5">No residents found.</td>
              </tr>
              <tr v-for="resident in filteredResidents" :key="resident.id">
                <td><strong>{{ resident.name }}</strong></td>
                <td>
                  <span :class="['pill', statusTone(resident.status)]">{{ resident.status }}</span>
                </td>
                <td>
                  <code v-if="resident.deviceId" class="bed-chip">{{ resident.deviceId }}</code>
                  <span v-else class="unassigned">Unassigned</span>
                </td>
                <td><span class="note-text">{{ resident.notes || '—' }}</span></td>
                <td>
                  <button class="entry-link" type="button" @click="openEditModal(resident)">Edit</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </section>

    <div v-if="modal.open" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <header class="modal-card__header">
          <div>
            <p class="modal-eyebrow">{{ modal.mode === 'edit' ? 'Edit resident' : 'New resident' }}</p>
            <h3 class="modal-title">{{ modal.mode === 'edit' ? 'Update resident info' : 'Create resident' }}</h3>
          </div>
          <button class="modal-close" type="button" @click="closeModal">
            <span class="material-symbols-outlined" aria-hidden="true">close</span>
          </button>
        </header>

        <div class="modal-form">
          <div class="form-group">
            <label class="form-label">Name *</label>
            <input v-model.trim="form.name" class="form-input" type="text" placeholder="Resident full name" maxlength="80" autocomplete="off" />
          </div>

          <div class="form-group">
            <label class="form-label">Status</label>
            <select v-model="form.status" class="form-input">
              <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Assigned Bed</label>
            <select v-model="form.deviceId" class="form-input">
              <option v-for="d in deviceOptions" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Notes</label>
            <input v-model.trim="form.notes" class="form-input" type="text" placeholder="Optional notes" maxlength="200" autocomplete="off" />
          </div>

          <footer class="modal-actions">
            <button class="action-button action-button--ghost" type="button" @click="closeModal">Cancel</button>
            <button class="action-button action-button--primary" type="button" :disabled="isSaving" @click="saveResident">
              {{ isSaving ? 'Saving...' : (modal.mode === 'edit' ? 'Save changes' : 'Create') }}
            </button>
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useResidentsPage } from '~/composables/residents/useResidentsPage'

useHead({ title: 'Clinical Sentinel | Residents' })

const {
  filteredResidents,
  deviceOptions,
  summaryCards,
  searchQuery,
  modal,
  form,
  isSaving,
  statusOptions,
  openCreateModal,
  openEditModal,
  closeModal,
  saveResident
} = useResidentsPage()

const statusTone = (status) => {
  if (status === 'Active') return 'pill--success'
  if (status === 'Monitoring') return 'pill--warning'
  return 'pill--neutral'
}
</script>

<style scoped>
.residents-page { display: grid; }

.residents-shell {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}









.pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pill--success { background: rgba(16, 185, 129, 0.18); color: #047857; }
.pill--warning { background: rgba(249, 115, 22, 0.18); color: #b45309; }
.pill--neutral { background: rgba(148, 163, 184, 0.18); color: #64748b; }

.bed-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #2559bd;
  border: 1px solid rgba(59, 130, 246, 0.24);
  font-size: 0.76rem;
  font-weight: 800;
}

.unassigned { color: var(--text-muted); font-size: 0.84rem; }
.note-text { color: var(--text-muted); font-size: 0.84rem; }

.entry-link {
  border: none;
  background: transparent;
  color: #2559bd;
  font-weight: 800;
  cursor: pointer;
  padding: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.modal-card {
  width: min(100%, 460px);
  border-radius: 20px;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  box-shadow: 0 28px 70px rgba(15, 23, 42, 0.22);
  overflow: hidden;
}

.modal-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 22px 18px;
  border-bottom: 1px solid var(--surface-border);
}

.modal-eyebrow {
  margin: 0 0 6px;
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #2559bd;
}

.modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 900;
  color: var(--text-main);
}

.modal-close {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: #475569;
  cursor: pointer;
}

.modal-form {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-label {
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--surface-border);
  background: var(--surface-panel-strong);
  color: var(--text-main);
  font-weight: 700;
  box-sizing: border-box;
  outline: none;
}

.form-input:focus { border-color: rgba(37, 89, 189, 0.34); }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 4px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 16px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.action-button:hover { transform: translateY(-1px); }
.action-button:disabled { opacity: 0.7; cursor: progress; transform: none; }

.action-button--primary {
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  color: #ffffff;
}

.action-button--ghost {
  background: var(--surface-panel-strong);
  color: var(--text-main);
  border-color: var(--surface-border);
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
  font-size: 1rem;
}

:global(.dark-mode) 
:global(.dark-mode) 
:global(.dark-mode) 
@media (max-width: 900px) {
  .summary-grid { grid-template-columns: 1fr; }
}
</style>
