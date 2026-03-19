<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-img">
          <img src="../images/logo.png" alt="Welltech Logo">
          <span class="brand-subtitle">IoT Health</span>
        </div>
        <p>Sistema de Monitoreo IoT</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="text" placeholder="Introduce tu usuario" :disabled="isLoading" required />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="password" type="password" placeholder="••••••••" :disabled="isLoading" required />
        </div>

        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          {{ isLoading ? 'Conectando...' : 'Iniciar Sesión' }}
        </button>
      </form>

      <div class="login-footer">
        <p>Acceso exclusivo para personal autorizado</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: false
})

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await auth.login(email.value, password.value)
    navigateTo('/')
  } catch (err) {
    errorMessage.value = 'Usuario o contraseña incorrectos'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 1.5rem; background: #020617; font-family: 'Inter', sans-serif; }
.login-card { background: #0f172a; padding: 40px; border-radius: 20px; width: 100%; max-width: 420px; border: 1px solid #1e293b; text-align: center; box-shadow: 0 18px 40px rgba(2, 6, 23, 0.45); }
.login-header p { color: #94a3b8; font-size: 14px; margin-top: 5px; margin-bottom: 30px; }
.form-group { text-align: left; margin-bottom: 20px; }
.form-group label { display: block; color: #94a3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
.form-group input { width: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid #334155; background: #020617; color: #f8fafc; outline: none; box-sizing: border-box; }
.form-group input:focus { border-color: #3b82f6; }
.btn-submit { width: 100%; padding: 14px; background: #3b82f6; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; transition: all 0.2s; }
.btn-submit:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.error-alert { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid rgba(239, 68, 68, 0.2); }
.login-footer p { color: #64748b; font-size: 11px; margin-top: 30px; }
.logo-img { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.logo-img img { max-width: 180px; height: auto; max-height: 60px; object-fit: contain; filter: brightness(1.18) contrast(1.05); }
.brand-subtitle { font-size: 0.75rem; color: #3b82f6; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
</style>
