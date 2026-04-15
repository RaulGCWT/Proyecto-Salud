import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

const RULES_API_BASE = 'http://localhost:3001/MonitoringRules'

const getOwnerId = () => {
  const auth = useAuthStore()
  return auth.user?.email || auth.user?.tenantKey || ''
}

const ownerHeaders = () => {
  const ownerId = getOwnerId()
  return ownerId ? { 'X-Owner-Id': ownerId } : {}
}

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: []
  }),
  actions: {
    async fetchRules() {
      try {
        const ownerId = getOwnerId()
        const data = await $fetch(RULES_API_BASE, {
          params: ownerId ? { ownerId } : {},
          headers: ownerHeaders()
        })
        this.rules = data || []
      } catch (err) {
        console.error('Error fetchRules:', err)
      }
    },
    async addRule(rule) {
      try {
        const ownerId = getOwnerId()
        await $fetch(RULES_API_BASE, {
          method: 'POST',
          headers: ownerHeaders(),
          body: {
            ownerId,
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
        const ownerId = getOwnerId()
        await $fetch(`${RULES_API_BASE}/${id}`, {
          method: 'PUT',
          headers: ownerHeaders(),
          body: {
            ownerId,
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
        const ownerId = getOwnerId()
        await $fetch(`${RULES_API_BASE}/${id}`, {
          method: 'DELETE',
          params: ownerId ? { ownerId } : {},
          headers: ownerHeaders()
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error deleteRule:', err)
      }
    }
  }
})
