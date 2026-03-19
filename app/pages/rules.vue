<template>
  <div class="rules-page">
    <header class="header">
      <h1 class="page-title">Monitoring Rules</h1>
      <button @click="openCreateModal" class="btn-primary tech-font">+ Add Rule</button>
    </header>

    <div class="list-container">
      <div v-if="rulesStore.rules.length === 0" class="empty tech-font">no_rules_active_in_system</div>
      
      <div v-for="rule in rulesStore.rules" :key="rule.id" class="card rule-card">
        <div class="rule-info">
          <strong class="rule-name tech-font">{{ rule.name }}</strong>
          <div class="value-box tech-font">
            {{ rule.variable.toUpperCase() }} {{ rule.operator }} {{ rule.value }}
          </div>
        </div>
        <div class="actions">
          <button @click="openEditModal(rule)" class="btn-action btn-edit tech-font">EDIT</button>
          <button @click="rulesStore.deleteRule(rule.id)" class="btn-action btn-del tech-font">DELETE</button>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="overlay">
      <div class="modal tech-modal">
        <h3 class="tech-font">{{ isEditing ? '> EDIT_RULE' : '> CREATE_RULE' }}</h3>
        
        <div class="form-group">
          <label class="tech-font">Rule Name</label>
          <input v-model="currentRule.name" class="tech-input tech-font" placeholder="e.g. Critical_Heart_Rate" />
        </div>

        <div class="grid">
          <div class="form-group">
            <label class="tech-font">Variable</label>
            <select v-model="currentRule.variable" class="tech-input tech-font">
              <option value="hr">Heart Rate</option>
              <option value="hrv">HRV</option>
              <option value="resp">Respiratory</option>
            </select>
          </div>
          <div class="form-group">
            <label class="tech-font">Operator</label>
            <select v-model="currentRule.operator" class="tech-input tech-font">
              <option value=">">Greater than</option>
              <option value="<">Less than</option>
            </select>
          </div>
          <div class="form-group">
            <label class="tech-font">Value</label>
            <input v-model="currentRule.value" type="number" class="tech-input tech-font" />
          </div>
        </div>

        <div class="modal-btns">
          <button @click="isModalOpen = false" class="btn-secondary tech-font">CANCEL</button>
          <button @click="save" class="btn-primary tech-font">SAVE_CHANGES</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRulesStore } from '~/stores/rules'

const rulesStore = useRulesStore()
const isModalOpen = ref(false)
const isEditing = ref(false)
const currentRuleId = ref(null)

const currentRule = ref({ name: '', variable: 'hr', operator: '>', value: 80 })

onMounted(() => rulesStore.fetchRules())

const openCreateModal = () => {
  isEditing.value = false
  currentRule.value = { name: '', variable: 'hr', operator: '>', value: 80 }
  isModalOpen.value = true
}

const openEditModal = (rule) => {
  isEditing.value = true
  currentRuleId.value = rule.id
  currentRule.value = { ...rule }
  isModalOpen.value = true
}

const save = async () => {
  if(currentRule.value.name) {
    if (isEditing.value) {
      await rulesStore.updateRule(currentRuleId.value, currentRule.value)
    } else {
      await rulesStore.addRule({...currentRule.value})
    }
    isModalOpen.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

.tech-font { font-family: 'JetBrains Mono', monospace; }

.rules-page { padding: 30px; max-width: 900px; margin: auto; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }

.btn-primary { 
  background: #3b82f6; color: white; border: none; padding: 10px 20px; 
  border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s;
}

.rule-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.rule-name { color: #3b82f6; font-size: 1.1rem; }

.value-box { 
  background: rgba(59, 130, 246, 0.05); padding: 8px 12px; border-radius: 6px;
  border-left: 3px solid #3b82f6; color: var(--text-main); font-size: 0.85rem;
}

.actions { display: flex; gap: 15px; }

.btn-action { background: none; border: 1px solid transparent; cursor: pointer; font-size: 0.75rem; padding: 5px 10px; border-radius: 4px; }
.btn-edit { color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); }
.btn-del { color: #ef4444; border-color: rgba(239, 68, 68, 0.3); }

/* ESTILOS DEL MODAL CORREGIDOS */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }

.tech-modal { 
  background: #ffffff; /* Fondo siempre blanco en modo claro */
  padding: 2.5rem; 
  border-radius: 12px; 
  width: 500px; 
  border: 1px solid #3b82f6; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.tech-modal h3 { color: #3b82f6; margin-bottom: 1.5rem; }

.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; font-size: 0.7rem; color: #3b82f6; text-transform: uppercase; margin-bottom: 6px; font-weight: bold; }

/* Input blanco por defecto */
.tech-input {
  width: 100%; 
  background: #ffffff; 
  border: 1px solid #cbd5e1; 
  padding: 12px; 
  border-radius: 8px; 
  color: #1e293b;
  outline: none;
}

/* Ajuste específico para Dark Mode */
:deep(.dark-mode) .tech-modal {
  background: #0f172a;
  border-color: #3b82f6;
}

:deep(.dark-mode) .tech-input {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

.grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 12px; }

.modal-btns { display: flex; justify-content: flex-end; gap: 12px; margin-top: 1.5rem; }
.btn-secondary { background: none; border: 1px solid #cbd5e1; color: #64748b; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
</style>