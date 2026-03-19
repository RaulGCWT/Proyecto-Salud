<template>
  <div class="profile-container">
    <h1 class="page-title">Mi Perfil</h1>
    
    <div class="card profile-card">
      <div class="profile-header">
        <div class="avatar-large">{{ auth.user?.name?.charAt(0) }}</div>
        <h2>{{ auth.user?.name }}</h2>
        <span class="badge">{{ auth.user?.groups[0] || 'Sin Grupo' }}</span>
      </div>

      <div class="profile-details">
        <div class="detail-item">
          <label>Email</label>
          <p>{{ auth.user?.email }}</p>
        </div>
        <div class="detail-item">
          <label>Tenant Key</label>
          <p><code>{{ auth.user?.tenantKey }}</code></p>
        </div>
        <div class="detail-item">
          <label>Grupos de Cognito</label>
          <div class="tags">
            <span v-for="group in auth.user?.groups" :key="group" class="tag">
              {{ group }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const auth = useAuthStore()
</script>

<style scoped>
.profile-card { max-width: 600px; margin: 0 auto; padding: 30px; }
.profile-header { text-align: center; margin-bottom: 30px; }
.avatar-large { 
  width: 80px; height: 80px; background: #3b82f6; color: white; 
  font-size: 2rem; border-radius: 50%; display: flex; 
  align-items: center; justify-content: center; margin: 0 auto 15px;
}
.detail-item { margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
.detail-item label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; }
.detail-item p { margin: 5px 0 0; font-weight: 500; }
.tag { 
  background: rgba(59, 130, 246, 0.1); color: #3b82f6; 
  padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; margin-right: 5px;
}
</style>