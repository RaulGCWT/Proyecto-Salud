<template>
  <div class="dashboard-wrapper" :class="{ 'dark-mode': isDark }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">⚡</div>
        <div class="logo-text"><h2>WELLTECH</h2><span>IoT Health</span></div>
      </div>
      
      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item" active-class="active">📊 Dashboard</NuxtLink>
        <NuxtLink to="/alerts" class="nav-item" active-class="active">⚠️ Alerts</NuxtLink>
        <NuxtLink to="/rules" class="nav-item" active-class="active">⚙️ Rules</NuxtLink>
        <NuxtLink to="/devices" class="nav-item" active-class="active">🛏️ Devices</NuxtLink>
        
        <button @click="toggleDark" class="mode-toggle">
          {{ isDark ? '☀️ Modo Claro' : '🌙 Modo Oscuro' }}
        </button>
      </nav>

      <div class="sidebar-footer">
        <p><strong>Admin_Health</strong></p>
        <button class="btn-logout" >Logout</button>
      </div>
    </aside>
    
    <main class="content-area">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useHealthStore } from '~/stores/health'

const health = useHealthStore()
const isDark = ref(false)

onMounted(() => { 
  health.connectWebSocket() 
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') isDark.value = true
})

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onUnmounted(() => {
  if (health.socket) health.socket.disconnect()
})
</script>

<style>
/* --- 1. VARIABLES --- */
:root {
  --bg-main: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
}

.dark-mode {
  --bg-main: #020617;
  --bg-card: #0f172a;   /* <-- CAMBIADO: Azul oscuro para tarjetas y gráfica */
  --text-main: #f1f5f9;  /* <-- CAMBIADO: Texto principal claro */
  --text-muted: #94a3b8;
  --border-color: #1e293b;
}

/* --- 2. ESTILOS BASE --- */
* { box-sizing: border-box; }

body { 
  margin: 0; 
  padding: 0; 
  font-family: 'Inter', sans-serif; 
  background-color: var(--bg-main) !important; 
  color: var(--text-main);
  transition: background-color 0.3s ease;
}

.dashboard-wrapper { display: flex; min-height: 100vh; }

.sidebar { 
  width: 260px; 
  background-color: #0f172a; 
  color: white; 
  height: 100vh; 
  position: fixed; 
  left: 0; top: 0; 
  display: flex; 
  flex-direction: column; 
  z-index: 100; 
}

.sidebar-header { padding: 24px; display: flex; align-items: center; gap: 12px; background-color: #020617; }
.logo-icon { background: #3b82f6; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; }
.sidebar-nav { flex: 1; padding: 20px 0; }
.nav-item { display: block; padding: 12px 24px; color: #94a3b8; text-decoration: none; transition: 0.2s; }
.nav-item:hover, .nav-item.active { color: white; background-color: rgba(59, 130, 246, 0.1); border-right: 4px solid #3b82f6; }

.mode-toggle {
  margin: 20px 24px;
  padding: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
}

.content-area { 
  margin-left: 260px; 
  padding: 40px; 
  width: calc(100% - 260px); 
  min-height: 100vh;
  background-color: var(--bg-main); 
}

.sidebar-footer { padding: 24px; border-top: 1px solid rgba(255,255,255,0.1); }
.btn-logout { width: 100%; padding: 8px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }

/* --- 3. INYECCIÓN PARA MODO OSCURO --- */

/* Aplicamos el fondo oscuro a tarjetas, gráfica y tablas */
.dark-mode .card, 
.dark-mode .chart-container,
.dark-mode .table-container {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-main) !important;
}

/* Títulos fuera de tarjetas */
.dark-mode h1, 
.dark-mode .page-title, 
.dark-mode .section-title {
  color: #ffffff !important;
}

.dark-mode .main-header p, 
.dark-mode .subtitle {
  color: var(--text-muted) !important;
}

/* BOTONES DE LA GRÁFICA: Ahora blancos porque el fondo de la gráfica es oscuro */
.dark-mode .control-btn {
  color: #ffffff !important; 
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid var(--border-color) !important;
}

/* Estilo para el botón pulsado (Azul) */
.dark-mode .control-btn.active {
  background: #3b82f6 !important; 
  color: #ffffff !important;
  border-color: #3b82f6 !important;
}

/* Etiquetas dentro de las tarjetas */
.dark-mode .card-label {
  color: var(--text-muted) !important;
}
</style>