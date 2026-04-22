import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import { getPreferredRuleAssignmentRole, getScopedOwnerId } from '~/utils/accessContext'

const RULES_API_BASE = 'http://localhost:3001/MonitoringRules'

const getUserOwnerId = () => {
  const auth = useAuthStore()
  return auth.user?.email || auth.user?.tenantKey || ''
}

const getScopeOwnerId = () => {
  const auth = useAuthStore()
  return getScopedOwnerId(auth.user || {})
}

const getUserRole = () => {
  const auth = useAuthStore()
  return getPreferredRuleAssignmentRole(auth.user || {}) || auth.user?.role || auth.user?.primaryGroup || ''
}

const scopedHeaders = () => {
  const ownerId = getScopeOwnerId()
  return ownerId ? { 'X-Owner-Id': ownerId } : {}
}

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: []
  }),
  actions: {
    async fetchRules() {
      try {
        const ownerId = getScopeOwnerId()
        const data = await $fetch(RULES_API_BASE, {
          params: ownerId ? { ownerId } : {},
          headers: scopedHeaders()
        })
        this.rules = data || []
      } catch (err) {
        console.error('Error fetchRules:', err)
      }
    },
    async addRule(rule) {
      try {
        const ownerId = getUserOwnerId()
        await $fetch(RULES_API_BASE, {
          method: 'POST',
          headers: {
            ...(getScopeOwnerId() ? { 'X-Owner-Id': getScopeOwnerId() } : {}),
            ...(getUserRole() ? { 'X-Role': getUserRole() } : {})
          },
          body: {
            ownerId,
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value),
            assignedToType: rule.assignedToType || 'none',
            assignedToId: rule.assignedToId || ''
          }
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error addRule:', err)
      }
    },
    async updateRule(id, rule) {
      try {
        const ownerId = getUserOwnerId()
        await $fetch(`${RULES_API_BASE}/${id}`, {
          method: 'PUT',
          headers: {
            ...(getScopeOwnerId() ? { 'X-Owner-Id': getScopeOwnerId() } : {}),
            ...(getUserRole() ? { 'X-Role': getUserRole() } : {})
          },
          body: {
            ownerId,
            name: rule.name,
            variable: rule.variable,
            operator: rule.operator,
            value: Number(rule.value),
            assignedToType: rule.assignedToType || 'none',
            assignedToId: rule.assignedToId || ''
          }
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error updateRule:', err)
      }
    },
    async deleteRule(id) {
      try {
        const ownerId = getScopeOwnerId()
        await $fetch(`${RULES_API_BASE}/${id}`, {
          method: 'DELETE',
          params: ownerId ? { ownerId } : {},
          headers: scopedHeaders()
        })
        await this.fetchRules()
      } catch (err) {
        console.error('Error deleteRule:', err)
      }
    }
  }
})
