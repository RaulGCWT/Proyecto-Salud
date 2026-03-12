import { defineStore } from 'pinia'

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: []
  }),
  actions: {
    async fetchRules() {
      try {
        const data = await $fetch('http://localhost:5000/rules')
        this.rules = data || []
      } catch (err) {
        console.error("Error fetchRules:", err)
      }
    },
    async addRule(rule) {
      try {
        await $fetch('http://localhost:5000/rules', {
          method: 'POST',
          body: {
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value)
          }
        })
        await this.fetchRules()
      } catch (err) {
        console.error("Error addRule:", err)
      }
    },
    // NUEVA ACCIÓN: EDITAR REGLA
    async updateRule(id, rule) {
      try {
        await $fetch(`http://localhost:5000/rules/${id}`, {
          method: 'PUT',
          body: {
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value)
          }
        })
        await this.fetchRules()
      } catch (err) {
        console.error("Error updateRule:", err)
      }
    },
    async deleteRule(id) {
      try {
        await $fetch(`http://localhost:5000/rules/${id}`, { method: 'DELETE' })
        await this.fetchRules()
      } catch (err) {
        console.error("Error deleteRule:", err)
      }
    }
  }
})