import { defineStore } from 'pinia'

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: [
      { id: 1, name: 'High Pulse', variable: 'hr', operator: '>', value: 100 },
      { id: 2, name: 'Low HRV', variable: 'hrv', operator: '<', value: 20 }
    ]
  }),
  actions: {
    addRule(rule) {
      this.rules.push({ ...rule, id: Date.now() })
    },
    deleteRule(id) {
      this.rules = this.rules.filter(r => r.id !== id)
    },
    updateRule(updatedRule) {
      const index = this.rules.findIndex(r => r.id === updatedRule.id)
      if (index !== -1) this.rules[index] = updatedRule
    }
  },
  persist: true
})