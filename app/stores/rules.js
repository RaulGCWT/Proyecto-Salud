import { defineStore } from 'pinia'

const RULES_API_BASE = 'http://localhost:3001/MonitoringRules'

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: []
  }),
  actions: {
    async fetchRules() {
      try {
        const data = await $fetch(RULES_API_BASE)
        this.rules = data || []
      } catch (err) {
        console.error('Error fetchRules:', err)
      }
    },
    async addRule(rule) {
      try {
        await $fetch(RULES_API_BASE, {
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
        console.error('Error addRule:', err)
      }
    },
    async updateRule(id, rule) {
      try {
        await $fetch(`${RULES_API_BASE}/${id}`, {
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
        console.error('Error updateRule:', err)
      }
    },
    async deleteRule(id) {
      try {
        await $fetch(`${RULES_API_BASE}/${id}`, { method: 'DELETE' })
        await this.fetchRules()
      } catch (err) {
        console.error('Error deleteRule:', err)
      }
    }
  }
})
