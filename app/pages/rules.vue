<template>
  <div class="rules-page">
    <header class="header">
      <h1>Monitoring Rules</h1>
      <button @click="isModalOpen = true" class="btn-primary">+ Add Rule</button>
    </header>

    <div class="list-container">
      <div v-if="rulesStore.rules.length === 0" class="empty">No rules active.</div>
      <div v-for="rule in rulesStore.rules" :key="rule.id" class="card">
        <div>
          <strong>{{ rule.name }}</strong>
          <p>{{ rule.variable.toUpperCase() }} {{ rule.operator }} {{ rule.value }}</p>
        </div>
        <button @click="rulesStore.deleteRule(rule.id)" class="btn-del">Delete</button>
      </div>
    </div>

    <div v-if="isModalOpen" class="overlay">
      <div class="modal">
        <h3>Create Rule</h3>
        <input v-model="newRule.name" placeholder="Rule Name" />
        <div class="grid">
          <select v-model="newRule.variable">
            <option value="hr">Heart Rate</option>
            <option value="hrv">HRV</option>
            <option value="resp">Respiratory</option>
          </select>
          <select v-model="newRule.operator">
            <option value=">">Greater than</option>
            <option value="<">Less than</option>
          </select>
        </div>
        <input v-model.number="newRule.value" type="number" placeholder="Threshold" />
        <div class="actions">
          <button @click="isModalOpen = false">Cancel</button>
          <button @click="save" class="btn-primary">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRulesStore } from '@/stores/rules'

const rulesStore = useRulesStore()
const isModalOpen = ref(false)
const newRule = ref({ name: '', variable: 'hr', operator: '>', value: 80 })

onMounted(() => rulesStore.fetchRules())

const save = async () => {
  if(newRule.value.name) {
    await rulesStore.addRule({...newRule.value})
    isModalOpen.value = false
    newRule.value = { name: '', variable: 'hr', operator: '>', value: 80 }
  }
}
</script>

<style scoped>
.rules-page { padding: 30px; max-width: 800px; margin: auto; font-family: sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; }
.btn-primary { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.list-container { margin-top: 20px; }
.card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; margin-bottom: 10px; }
.btn-del { color: #ef4444; background: none; border: none; cursor: pointer; }
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
.modal { background: white; padding: 25px; border-radius: 12px; width: 350px; display: flex; flex-direction: column; gap: 15px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
input, select { padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; }
.actions { display: flex; justify-content: flex-end; gap: 10px; }
.empty { text-align: center; color: #94a3b8; margin-top: 40px; }
</style>