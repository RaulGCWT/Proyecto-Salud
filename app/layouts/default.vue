<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">⚡</div>
        <div class="logo-text"><h2>WELLTECH</h2><span>IoT Health</span></div>
      </div>
      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item" active-class="active">📊 Dashboard</NuxtLink>
        <NuxtLink to="/alerts" class="nav-item" active-class="active">⚠️ Alerts</NuxtLink>
        <NuxtLink to="/rules" class="nav-item" active-class="active">⚙️ Rules</NuxtLink>
      </nav>
      <div class="sidebar-footer">
        <p><strong>Admin_Health</strong></p>
        <button class="btn-logout">Logout</button>
      </div>
    </aside>
    <main class="content-area"><slot /></main>
  </div>
</template>

<script setup>
import { useHealthStore } from '~/stores/health'
const health = useHealthStore()
let timer
onMounted(() => { timer = setInterval(() => { health.updateSensors() }, 3000) })
onUnmounted(() => clearInterval(timer))
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
.dashboard-wrapper { display: flex; }
.sidebar { width: 260px; background-color: #0f172a; color: white; height: 100vh; position: fixed; left: 0; top: 0; display: flex; flex-direction: column; z-index: 100; }
.sidebar-header { padding: 24px; display: flex; align-items: center; gap: 12px; background-color: #020617; }
.logo-icon { background: #3b82f6; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; }
.sidebar-nav { flex: 1; padding: 20px 0; }
.nav-item { display: block; padding: 12px 24px; color: #94a3b8; text-decoration: none; border-left: 4px solid transparent; }
.nav-item.active { border-left: 4px solid #3b82f6; background-color: #1e293b; color: white; }
.sidebar-footer { padding: 24px; border-top: 1px solid #1e293b; }
.btn-logout { width: 100%; padding: 10px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer; }
.content-area { margin-left: 260px; width: calc(100% - 260px); padding: 40px; min-height: 100vh; }
.main-header { margin-bottom: 32px; }
</style>