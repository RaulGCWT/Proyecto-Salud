<template>
  <div class="dashboard-wrapper" :class="{ 'dark-mode': isDark }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-img">
          <img src="../images/logo.png" alt="Welltech Logo">
          <span class="brand-subtitle">IoT Health</span>
        </div>
      </div>
      
      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item" active-class="active">📊 Dashboard</NuxtLink>
        <NuxtLink to="/profile" class="nav-item" active-class="active">👤 My profile</NuxtLink>
        <NuxtLink to="/alerts" class="nav-item" active-class="active">⚠️ Alerts</NuxtLink>
        <NuxtLink to="/rules" class="nav-item" active-class="active">⚙️ Rules</NuxtLink>
        <NuxtLink to="/devices" class="nav-item" active-class="active">🛏️ Devices</NuxtLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-row">
          <p class="user-display"><strong>{{ displayUserName }}</strong></p>
          <button @click="toggleDark" class="mini-mode-toggle" :title="isDark ? 'Modo Claro' : 'Modo Oscuro'">
            {{ isDark ? '☀️' : '🌙' }}
          </button>
        </div>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </aside>
    
    <main class="content-area">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useHealthStore } from '~/stores/health'
import { useAuthStore } from '~/stores/auth'

const health = useHealthStore()
const auth = useAuthStore() 
const isDark = ref(false)

const displayUserName = computed(() => {
  return auth.user?.name || 'Invitado'
})

onMounted(() => { 
  health.connectWebSocket() 
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') isDark.value = true
})

const handleLogout = () => {
  auth.logout()
}

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onUnmounted(() => {
  if (health.socket) health.socket.disconnect()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
  --bg-main: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
}

.dark-mode {
  --bg-main: #020617;
  --bg-card: #0f172a;  
  --text-main: #f1f5f9; 
  --text-muted: #94a3b8;
  --border-color: #1e293b;
}

body { 
  margin: 0; font-family: 'Inter', sans-serif; 
  background-color: var(--bg-main) !important; color: var(--text-main);
  transition: background-color 0.3s ease;
}

.dashboard-wrapper { display: flex; min-height: 100vh; }

.sidebar { 
  width: 260px; background-color: #0f172a; color: white; 
  height: 100vh; position: fixed; left: 0; top: 0; 
  display: flex; flex-direction: column; z-index: 100; 
}

.sidebar-header { 
  padding: 20px; 
  background-color: #020617; 
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.logo-img { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.logo-img img { 
  max-width: 180px; height: auto; max-height: 60px;
  object-fit: contain; filter: brightness(1.1);
}

.brand-subtitle {
  font-size: 0.75rem; color: #3b82f6;
  text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;
}

.sidebar-nav { flex: 1; padding: 20px 0; }
.nav-item { display: block; padding: 12px 24px; color: #94a3b8; text-decoration: none; transition: 0.2s; }
.nav-item:hover, .nav-item.active { color: white; background-color: rgba(59, 130, 246, 0.1); border-right: 4px solid #3b82f6; }

.content-area { 
  margin-left: 260px; padding: 40px; width: calc(100% - 260px); 
  min-height: 100vh; background-color: var(--bg-main); 
}

/* ESTILOS DEL FOOTER Y BOTÓN */
.sidebar-footer { padding: 24px; border-top: 1px solid rgba(255,255,255,0.1); }

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.user-display {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: #3b82f6;
  margin: 0;
}

.mini-mode-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.btn-logout { 
  width: 100%; padding: 8px; background: #ef4444; color: white; 
  border: none; border-radius: 6px; cursor: pointer; 
}

/* --- MODO OSCURO (SIN CAMBIOS) --- */
.dark-mode h1, .dark-mode h2, .dark-mode h3, .dark-mode h4, .dark-mode .page-title {
  color: #ffffff !important;
}

.dark-mode .card, .dark-mode .chart-container, .dark-mode .table-container {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-main) !important;
}

.dark-mode .value-box {
  color: #f1f5f9 !important;
}
</style>