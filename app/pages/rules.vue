<template>
  <div class="rules-page">
    <header class="header">
      <h1>Monitoring Rules</h1>
      <button @click="openCreateModal" class="btn-primary">+ Add Rule</button>
    </header>

    <div class="list-container">
      <div v-if="rulesStore.rules.length === 0" class="empty">No rules active.</div>
      <div v-for="rule in rulesStore.rules" :key="rule.id" class="card">
        <div>
          <strong>{{ rule.name }}</strong>
          <p>{{ rule.variable.toUpperCase() }} {{ rule.operator }} {{ rule.value }}</p>
        </div>
        <div class="actions">
          <button @click="openEditModal(rule)" class="btn-edit">Edit</button>
          <button @click="rulesStore.deleteRule(rule.id)" class="btn-del">Delete</button>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="overlay">
      <div class="modal">
        <h3>{{ isEditing ? 'Edit Rule' : 'Create Rule' }}</h3>
        <input v-model="currentRule.name" placeholder="Rule Name" />
        <div class="grid">
          <select v-model="currentRule.variable">
            <option value="hr">Heart Rate</option>
            <option value="hrv">HRV</option>
            <option value="resp">Respiratory</option>
          </select>
          <select v-model="currentRule.operator">
            <option value=">">Greater than</option>
            <option value="<">Less than</option>
          </select>
          <input v-model="currentRule.value" type="number" placeholder="Value" />
        </div>
        <div class="modal-btns">
          <button @click="isModalOpen = false">Cancel</button>
          <button @click="save" class="btn-primary">Save</button>
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
  currentRule.value = { ...rule } // Copiamos los datos de la regla al formulario
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
/* Mantengo tus estilos y solo añado los de los botones nuevos */
.rules-page { padding: 30px; max-width: 800px; margin: auto; font-family: sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; }
.btn-primary { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.list-container { margin-top: 20px; }
.card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; margin-bottom: 10px; }
.actions { display: flex; gap: 10px; align-items: center; }
.btn-edit { color: #2563eb; background: none; border: none; cursor: pointer; font-weight: bold; }
.btn-del { color: #ef4444; background: none; border: none; cursor: pointer; }
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
.modal { background: white; padding: 25px; border-radius: 12px; width: 400px; }
.grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 15px 0; }
.modal-btns { display: flex; justify-content: flex-end; gap: 10px; }
input, select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
</style>