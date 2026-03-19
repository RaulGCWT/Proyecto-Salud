<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-circle">⚡</div>
        <h1>WELLTECH</h1>
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
    // Al usar await auth.login, el store ya tiene los datos antes de navegar
    navigateTo('/')
  } catch (err) {
    errorMessage.value = "Usuario o contraseña incorrectos"
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 1.5rem; background: var(--bg-main); font-family: 'Inter', sans-serif; }
.login-card { background: var(--bg-card); padding: 40px; border-radius: 20px; width: 100%; max-width: 420px; border: 1px solid var(--border-color); text-align: center; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }
.logo-circle { background: #3b82f6; width: 60px; height: 60px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 15px; }
.login-header h1 { color: var(--text-main); margin: 0; font-size: 24px; letter-spacing: 2px; }
.login-header p { color: var(--text-muted); font-size: 14px; margin-top: 5px; margin-bottom: 30px; }
.form-group { text-align: left; margin-bottom: 20px; }
.form-group label { display: block; color: var(--text-muted); font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
.form-group input { width: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-main); outline: none; box-sizing: border-box; }
.form-group input:focus { border-color: #3b82f6; }
.btn-submit { width: 100%; padding: 14px; background: #3b82f6; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; transition: all 0.2s; }
.btn-submit:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.error-alert { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid rgba(239, 68, 68, 0.2); }
.login-footer p { color: var(--text-muted); font-size: 11px; margin-top: 30px; }
</style>
