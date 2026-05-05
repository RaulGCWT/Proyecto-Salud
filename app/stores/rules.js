import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import { buildBackendAuthHeaders } from '~/utils/backendAuth'

const RULES_API_BASE = 'http://localhost:5000/rules'

const scopedHeaders = () => {
  return buildBackendAuthHeaders(useAuthStore())
}

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: []
  }),
  actions: {
    async fetchRules() {
      try {
        const data = await $fetch(RULES_API_BASE, { headers: scopedHeaders() })
        this.rules = data || []
      } catch (err) {
        console.error('Error fetchRules:', err)
      }
    },
    async addRule(rule) {
      try {
        await $fetch(RULES_API_BASE, {
          method: 'POST',
          headers: scopedHeaders(),
          body: {
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value),
            assignedToType: rule.assignedToType || 'none',
            assignedToId: rule.assignedToId || '',
            assignedToSide: rule.assignedToSide || 'all'
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
          headers: scopedHeaders(),
          body: {
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value),
            assignedToType: rule.assignedToType || 'none',
            assignedToId: rule.assignedToId || '',
            assignedToSide: rule.assignedToSide || 'all'
          }
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error updateRule:', err)
      }
    },
    async deleteRule(id) {
      try {
        await $fetch(`${RULES_API_BASE}/${id}`, {
          method: 'DELETE',
          headers: scopedHeaders()
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error deleteRule:', err)
      }
    }
  }
})
