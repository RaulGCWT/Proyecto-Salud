<template>
  <div class="profile-page">
    <h1 class="page-title">User System Info</h1>
    
    <div class="card profile-card">
      <div class="profile-header">
        <div class="user-avatar">{{ auth.user?.name?.charAt(0) }}</div>
        <div class="info-item">
          <label class="tech-font">Full Name</label>
          <div class="value-box tech-font">{{ auth.user?.name || 'Unknown User' }}</div>
        </div>
        
        <div class="info-item">
          <label class="tech-font">Service Email</label>
          <div class="value-box tech-font">{{ auth.user?.email || 'N/A' }}</div>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <label class="tech-font">Your company</label>
          <div class="value-box tech-font">{{ auth.user?.tenantKey || 'N/A' }}</div>
        </div>

        <div class="info-item">
          <label class="tech-font">Your role</label>
          <div class="groups-list">
            <span v-for="group in auth.user?.groups" :key="group" class="group-tag tech-font">
              {{ group }}
            </span>
            <span v-if="!auth.user?.groups?.length" class="tech-font no-data">no_groups_found</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Asegúrate de tener jwt-decode instalado para que auth.js no de error
const auth = useAuthStore()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

.tech-font {
  font-family: 'JetBrains Mono', monospace;
}

.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card { 
  background: var(--bg-card); 
  padding: 2.5rem; 
  border-radius: 12px; 
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.profile-header { 
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border-color);
}

.user-avatar { 
  width: 70px; height: 70px; background: #3b82f6; color: white; 
  border-radius: 12px; display: flex; align-items: center; 
  justify-content: center; font-size: 1.8rem; margin: 0 auto 1.5rem;
  font-family: 'JetBrains Mono', monospace;
}

.info-item { margin-top: 1.5rem; text-align: left; }

.info-item label { 
  display: block; 
  font-size: 0.75rem; 
  color: #3b82f6; 
  text-transform: uppercase; 
  margin-bottom: 0.6rem;
  font-weight: bold;
}

.value-box { 
  background: rgba(59, 130, 246, 0.05); 
  padding: 12px; 
  border-radius: 6px; 
  border-left: 3px solid #3b82f6;
  color: var(--text-main);
  font-size: 0.85rem;
  word-break: break-all;
}

.group-tag { 
  display: inline-block;
  background: #1e293b; 
  color: #3b82f6; 
  padding: 5px 12px; 
  border-radius: 4px; 
  font-size: 0.75rem; 
  margin: 0 8px 8px 0;
  border: 1px solid #3b82f640;
}

.no-data { color: var(--text-muted); font-size: 0.8rem; font-style: italic; }
</style>