<template>
  <div class="rules-page">
    <header class="header">
      <h1>Monitoring Rules</h1>
      <button @click="isModalOpen = true" class="btn-add">Add New Rule</button>
    </header>

    <div class="rules-list">
      <div v-for="rule in store.rules" :key="rule.id" class="rule-card">
        <div>
          <h3>{{ rule.name }}</h3>
          <p>{{ rule.variable.toUpperCase() }} {{ rule.operator }} {{ rule.value }}</p>
        </div>
        <button @click="store.deleteRule(rule.id)" class="btn-delete">Delete</button>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-content">
        <h2>New Rule</h2>
        <input v-model="newRule.name" placeholder="Rule Name" class="input" />
        <div class="row">
          <select v-model="newRule.variable">
            <option value="hr">HR</option>
            <option value="hrv">HRV</option>
            <option value="resp">Resp</option>
          </select>
          <select v-model="newRule.operator">
            <option value=">">></option>
            <option value="<"><</option>
          </select>
          <input v-model.number="newRule.value" type="number" class="input" />
        </div>
        <div class="actions">
          <button @click="isModalOpen = false" class="btn-cancel">Cancel</button>
          <button @click="save" class="btn-add">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRulesStore } from '~/stores/rules'
const store = useRulesStore()
const isModalOpen = ref(false)
const newRule = ref({ name: '', variable: 'hr', operator: '>', value: 100 })

const save = () => {
  if (newRule.value.name) {
    store.addRule(newRule.value)
    isModalOpen.value = false
    newRule.value = { name: '', variable: 'hr', operator: '>', value: 100 }
  }
}
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.btn-add { background: #0f172a; color: white; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; }
.rules-list { display: grid; gap: 15px; }
.rule-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; justify-content: space-between; }
.btn-delete { color: #ef4444; border: none; background: none; cursor: pointer; font-weight: bold; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal-content { background: white; padding: 30px; border-radius: 16px; width: 400px; display: flex; flex-direction: column; gap: 15px; }
.row { display: flex; gap: 10px; }
.input, select { padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; width: 100%; }
.btn-cancel { background: #f1f5f9; border: none; padding: 10px; border-radius: 8px; cursor: pointer; }
</style>